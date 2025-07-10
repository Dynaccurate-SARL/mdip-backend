from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.drug_catalog_dto import CountryCode
from src.application.use_cases.drug_catalog.import_task import CatalogImportUseCase
from src.config.settings import Envs
from src.infrastructure.repositories.icatalog_transaction_repository import ICatalogTransactionRepository
from src.infrastructure.repositories.idrug_catalog_repository import IDrugCatalogRepository
from src.infrastructure.repositories.idrug_repository import IDrugRepository
from src.infrastructure.services.blob_storage import get_file
from src.infrastructure.services.confidential_ledger import ledger_builder
from src.infrastructure.services.pandas_parser.drug.impl import drug_parser_factory


class ParseTaskData(BaseModel):
    catalog_id: int
    filename: str
    parser: CountryCode


async def task(session: AsyncSession, data: ParseTaskData, config: Envs):
    file_path = await get_file(data.filename, config)

    FileParser = drug_parser_factory(data.parser)
    drug_catalog_repository = IDrugCatalogRepository(session)
    transaction_repository = ICatalogTransactionRepository(session)
    drug_repository = IDrugRepository(session)
    ledger_service = ledger_builder(
        config.AZURE_LEDGER_URL, 
        config.AZURE_LEDGER_CERTIFICATE_PATH,
        config.AZURE_CREDENTIAL_TENNANT_ID,
        config.AZURE_CREDENTIAL_CLIENT_ID,
        config.AZURE_CREDENTIAL_CERTIFICATE_PATH,
        config.ENVIRONMENT
    )

    use_case = CatalogImportUseCase(
        drug_catalog_repository=drug_catalog_repository,
        transaction_repository=transaction_repository,
        drug_repository=drug_repository,
        ledger_service=ledger_service,
        catalog_id=data.catalog_id,
        parser=FileParser(file_path),
        session=session,
    )
    await use_case.prepare_transaction_data(data.filename, file_path)
    await use_case.execute()
