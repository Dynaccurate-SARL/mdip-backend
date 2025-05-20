import uuid
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.mapping import CentralDrugMappingDto
from src.application.use_cases.mapping.create import MappingCheckUseCase
from src.application.use_cases.mapping.import_task import MappingImportUseCase
from src.application.use_cases.mapping.mappings_by_drug_id import DrugMappingsUseCase
from src.config.settings import get_config
from src.domain.entities.user import User
from src.domain.services.auth_service import manager
from src.infrastructure.db.base import IdInt
from src.infrastructure.db.engine import get_session
from src.infrastructure.repositories.idrug_catalog_repository import IDrugCatalogRepository
from src.infrastructure.repositories.idrug_repository import IDrugRepository
from src.infrastructure.repositories.imapping_repository import IMappingRepository
from src.infrastructure.repositories.imapping_transaction_repository import IMappingTransactionRepository
from src.infrastructure.services.blob_storage.azure_storage import AzureFileService
from src.infrastructure.services.blob_storage.disk_storage import DiskFileService
from src.infrastructure.services.confidential_ledger import ledger_builder
from src.infrastructure.services.pandas_parser.drug.exc import InvalidFileFormat
from src.infrastructure.services.pandas_parser.mapping.parse import MappingParser
from src.utils.exc import ResourceNotFound


mapping_router = APIRouter()


@mapping_router.get(
    "/mappings/{drug_id}", response_model=CentralDrugMappingDto,
    summary="Get mappings related to a drug by its ID")
async def get_mappings(
        drug_id: IdInt,
        session: Annotated[AsyncSession, Depends(get_session)]):
    # Prepare the repository and service for the use case
    drug_catalog_repository = IDrugCatalogRepository(session)
    drug_repository = IDrugRepository(session)
    mapping_repository = IMappingRepository(session)

    usecase = DrugMappingsUseCase(
        drug_catalog_repository, drug_repository, mapping_repository)
    try:
        return await usecase.execute(drug_id)
    except ResourceNotFound as err:
        return err.as_response(status_code=status.HTTP_404_NOT_FOUND)


async def mapping_import_task(use_case: MappingImportUseCase):
    await use_case.execute()


@mapping_router.post(
    "/mappings", summary="Import drug mappings from a mapping file")
async def mapping_upload(
        background_tasks: BackgroundTasks,
        user: Annotated[User, Depends(manager)],
        session: Annotated[AsyncSession, Depends(get_session)],
        # http form data
        file: Annotated[UploadFile, File(...)],
        catalog_to_id: Annotated[IdInt, Query(examples=["1.0"])]):
    try:
        file_bytes = await file.read()
        parser = MappingParser(file_bytes)
    except InvalidFileFormat as err:
        return err.as_response(status_code=status.HTTP_400_BAD_REQUEST)

    # Prepare the repository and service for the mapping use case
    drug_catalog_repository = IDrugCatalogRepository(session)

    # check if the requirements to import the mapping file is valid
    try:
        mapping_use_case = MappingCheckUseCase(drug_catalog_repository)
        result = await mapping_use_case.execute(catalog_to_id)
    except ResourceNotFound as err:
        return err.as_response(status_code=status.HTTP_400_BAD_REQUEST)

    # rename filename to ensure uniqueness
    file.filename = f"{str(uuid.uuid4())}_{file.filename}"

    # Upload file to the appropriate storage strategy
    if get_config().UPLOAD_STRATEGY == "AZURE":
        AzureFileService(
            get_config().AZURE_BLOB_CONTAINER_NAME,
            get_config().AZURE_BLOB_STORAGE_CONNECTION_STRING
        ).upload_file(file.filename, file.file.read())
    if get_config().UPLOAD_STRATEGY == "DISK":
        DiskFileService(get_config().DOCUMENTS_STORAGE_PATH).upload_file(
            file.filename, file.file.read())

    # Prepare the dependencies for the import task use case
    transaction_repository = IMappingTransactionRepository(session)
    mapping_repository = IMappingRepository(session)
    drug_repository = IDrugRepository(session)
    ledger_service = ledger_builder(
        get_config().AZURE_LEDGER_URL,
        get_config().AZURE_CERTIFICATE_PATH
    )

    use_case = MappingImportUseCase(
        drug_repository=drug_repository,
        transaction_repository=transaction_repository,
        mapping_repository=mapping_repository,
        ledger_service=ledger_service,
        mapping_parser=parser,
        mapping_id=result.mapping_id,
        central_catalog_id=result.central_catalog_id,
        related_catalog_id=catalog_to_id
    )
    await use_case.prepare_task(file)
    # Add task to be processed in the background tasks
    background_tasks.add_task(
        mapping_import_task,
        use_case=use_case
    )

    return JSONResponse(
        status_code=201, content={'detail': 'mapping created successfully'})
