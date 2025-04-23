from src.domain.entities.drug_catalog import DrugCatalog
from src.domain.entities.drug_mapping import DrugMapping
from src.infrastructure.repositories.contract import DrugRepositoryInterface, MappingRepositoryInterface
from src.infrastructure.services.confidential_ledger.contract import Ledger, TransactionData
from src.infrastructure.services.pandas_parser.mapping.parse import MappingParser


class MappingImportUseCase:
    def __init__(self, drug_repository: DrugRepositoryInterface,
                 mapping_repository: MappingRepositoryInterface,
                 mapping_parser: MappingParser, ledger_service: Ledger,
                 central_catalog_id: int, catalog_to_id: int):
        self._drug_repository = drug_repository
        self._mapping_repository = mapping_repository
        self._ledger_service = ledger_service
        self._mapping_parser = mapping_parser
        self._central_catalog_id = central_catalog_id
        self._catalog_to_id = catalog_to_id

    async def execute(self):
        transaction_data = TransactionData(
            entity_name=DrugCatalog.__tablename__,
            entity_id=self._catalog_to_id,
            status='processing',
            data={
                'type': 'mapping_import',
                'catalog_central_id': self._central_catalog_id,
                'catalog_to_id': self._catalog_to_id,
            }
        )

        print(
            f"Mapping import process started for catalog_id={self._central_catalog_id}")
        await self._ledger_service.insert_transaction(transaction_data)

        for mappings in self._mapping_parser.parse():
            for mapping in mappings:
                central_catalog_drug = await self._drug_repository.\
                    get_by_drug_code_on_catalog_id(
                        self._central_catalog_id, mapping.drug_code)
                if central_catalog_drug:
                    related_catalog_drug = await self._drug_repository.\
                        get_by_drug_code_on_catalog_id(
                            self._catalog_to_id, mapping.related_drug_code)

                    mapping = DrugMapping(
                        drug_id=central_catalog_drug._id,
                        related_drug_id=related_catalog_drug._id)
                    await self._mapping_repository.save(mapping)

        transaction_data.status = 'completed'
        print(
            f"Mapping import process completed for catalog_id={self._central_catalog_id}")
        await self._ledger_service.insert_transaction(transaction_data)

        await self._drug_repository.close_session()
