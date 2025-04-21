from src.config.settings import get_config
from src.infrastructure.repositories.contract import LedgerTransactionRepositoryInterface
from src.infrastructure.services.confidential_ledger.contract import Ledger
from src.infrastructure.services.confidential_ledger.iazure_ledger import AzureLedger
from src.infrastructure.services.confidential_ledger.idb_ledger import DBLedgerService


def get_confidential_ledger(
        db_lt_repository: LedgerTransactionRepositoryInterface,
        azure_ledger_url: str,
        azure_ledger_certificate_path: str,
) -> Ledger:
    if get_config().ENVIRONMENT == 'PROD':
        return AzureLedger(
            azure_ledger_url, azure_ledger_certificate_path, db_lt_repository)
    return DBLedgerService(db_lt_repository)
