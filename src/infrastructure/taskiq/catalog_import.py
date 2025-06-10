from pydantic import BaseModel

from src.application.dto.drug_catalog_dto import CountryCode
from src.application.use_cases.drug_catalog.import_task import CatalogImportUseCase
from src.config.settings import get_config
from src.infrastructure.db.engine import AsyncLocalSession
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


async def task(data: dict):
    data: ParseTaskData = ParseTaskData.model_validate(data)

    filepath = await get_file(data.filename)

    async with AsyncLocalSession() as session:
        FileParser = drug_parser_factory(data.parser)
        drug_catalog_repository = IDrugCatalogRepository(session)
        transaction_repository = ICatalogTransactionRepository(session)
        drug_repository = IDrugRepository(session)
        ledger_service = ledger_builder(
            get_config().AZURE_LEDGER_URL, get_config().AZURE_CERTIFICATE_PATH
        )

        use_case = CatalogImportUseCase(
            drug_catalog_repository=drug_catalog_repository,
            transaction_repository=transaction_repository,
            drug_repository=drug_repository,
            ledger_service=ledger_service,
            catalog_id=data.catalog_id,
            parser=FileParser(filepath),
            session=session,
        )
        await use_case.prepare_transaction_data(data.filename, filepath)
        await use_case.execute()
