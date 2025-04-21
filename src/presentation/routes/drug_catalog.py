import uuid
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi import Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.drug_catalog_dto import (
    CountryCode, DrugCatalogCreateDto, DrugCatalogCreatedDto, DrugCatalogDto, DrugCatalogPaginatedDto)
from src.application.use_cases.drug_catalog.get_drug_catalog_by_id import GetDrugCatalogByIdUseCase
from src.application.use_cases.drug_catalog.get_paginated_drug_catalog import GetPaginatedDrugCatalogUseCase
from src.application.use_cases.drug_catalog.import_task import CatalogImportUseCase
from src.config.settings import get_config
from src.domain.entities.user import User
from src.domain.services.auth_service import manager
from src.infrastructure.db.base import IdInt
from src.infrastructure.db.engine import get_session
from src.infrastructure.repositories.idrug_catalog_repository import IDrugCatalogRepository
from src.infrastructure.repositories.iledger_transaction_repository import ILedgerTransactionRepository
from src.application.use_cases.drug_catalog.drug_catalog_create import DrugCatalogCreateUseCase
from src.infrastructure.services.blob_storage.azure_storage import AzureFileService
from src.infrastructure.services.blob_storage.disk_storage import DiskFileService
from src.infrastructure.services.pandas_parser.drug.exc import InvalidFileFormat
from src.infrastructure.services.pandas_parser.drug.impl import drug_parser_factory
from src.infrastructure.services.confidential_ledger import get_confidential_ledger
from src.utils.exc import ConflictErrorCode


drug_catalog_router = APIRouter()


@drug_catalog_router.get("/catalogs/{catalog_id}",
                         status_code=status.HTTP_200_OK,
                         response_model=DrugCatalogDto)
async def get_catalog_by_id(
        session: Annotated[AsyncSession, Depends(get_session)],
        catalog_id: IdInt):
    # Prepare the repository
    drug_catalog_repository = IDrugCatalogRepository(session)

    # Fetch the catalog by ID
    use_case = GetDrugCatalogByIdUseCase(drug_catalog_repository)
    drug_catalog = await use_case.execute(catalog_id)
    if not drug_catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drug catalog not found"
        )
    return drug_catalog


@drug_catalog_router.get("/p/catalogs",
                         status_code=status.HTTP_200_OK,
                         response_model=DrugCatalogPaginatedDto)
async def get_catalogs(
        session: Annotated[AsyncSession, Depends(get_session)],
        page: Annotated[int, Query(gt=0, example=1)] = 1,
        psize: Annotated[int, Query(gt=0, example=10)] = 10,
        name: Annotated[str, Query(...)] = ''):
    # Prepare the repository
    drug_catalog_repository = IDrugCatalogRepository(session)

    # Fetch paginated catalogs
    use_case = GetPaginatedDrugCatalogUseCase(drug_catalog_repository)
    return await use_case.execute(page, psize, name)


async def drug_catalog_import_task(usecase: CatalogImportUseCase):
    await usecase.execute()


@drug_catalog_router.post("/catalogs",
                          status_code=status.HTTP_201_CREATED,
                          response_model=DrugCatalogCreatedDto)
async def create_catalog(
        background_tasks: BackgroundTasks,
        user: Annotated[User, Depends(manager)],
        session: Annotated[AsyncSession, Depends(get_session)],
        # http form data
        file: Annotated[UploadFile, File(...)],
        name: Annotated[str, Form(examples=["Pharmaceutical Catalog"])],
        country: Annotated[CountryCode, Form(examples=["US"])],
        version: Annotated[str, Form(examples=["1.0"])],
        is_central: Annotated[bool, Form(...)] = False,
        notes: Annotated[str, Form(examples=["Initial release"])] = ''):
    try:
        file_bytes = await file.read()
        parser = drug_parser_factory(country, file_bytes)
    except InvalidFileFormat as err:
        return err.as_response(status_code=status.HTTP_400_BAD_REQUEST)

    # rename filename to ensure uniqueness
    file.filename = f"{str(uuid.uuid4())}_{file.filename}"

    # Upload file to the appropriate storage strategy
    if get_config().UPLOAD_STRATEGY == "AZURE":
        AzureFileService(
            get_config().AZURE_BLOB_CONTAINER_NAME,
            get_config().AZURE_BLOB_STORAGE_CONNECTION_STRING).upload_file(
            file.filename, file.file.read())
    if get_config().UPLOAD_STRATEGY == "DISK":
        DiskFileService(get_config().DOCUMENTS_STORAGE_PATH).upload_file(
            file.filename, file.file.read())

    # Prepare the repository and service for the use case
    drug_catalog_repository = IDrugCatalogRepository(session)
    lt_repository = ILedgerTransactionRepository(session)
    ledger_service = get_confidential_ledger(
        lt_repository,
        get_config().AZURE_LEDGER_URL,
        get_config().AZURE_CERTIFICATE_PATH
    )

    try:
        # Create a new drug catalog entry in the database and ledger
        drug_catalog_use_case = DrugCatalogCreateUseCase(
            drug_catalog_repository,
            ledger_service
        )
        data = DrugCatalogCreateDto(
            name=name,
            country=country,
            version=version,
            notes=notes,
            is_central=is_central,
            file=file
        )
        drug_catalog = await drug_catalog_use_case.execute(data)

        CatalogImportUseCase(
            catalog_id=drug_catalog.id,
            parser=parser,
            session=session,
            ledger_service=ledger_service
        )
        background_tasks.add_task(
            drug_catalog_import_task,
            usecase=CatalogImportUseCase
        )

        return drug_catalog
    except ConflictErrorCode as e:
        return e.as_response(status_code=status.HTTP_409_CONFLICT)
