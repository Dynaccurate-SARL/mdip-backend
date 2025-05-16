
import os
from uuid import uuid4
from unittest.mock import Mock

from src.infrastructure.services.confidential_ledger.azure_ledger import AzureLedger
from src.infrastructure.services.confidential_ledger.contract import (
    LedgerInterface, TransactionInserted)


def _fake_azure_ledger():
    def _fake(*args, **kwargs):
        return TransactionInserted(
            status='ready',
            transaction_id=uuid4(),
            transaction_data={'data': 'fake_data'}
        )
    fake = Mock(spec=LedgerInterface)
    fake.insert_transaction.side_effect = _fake
    fake.retrieve_transaction.return_value = _fake
    return fake


def ledger_builder(azure_ledger_url: str, 
                   azure_ledger_certificate_path: str) -> LedgerInterface:
    if os.getenv('ENVIRONMENT', None) == 'PROD':
        return AzureLedger(
            azure_ledger_url, azure_ledger_certificate_path)
    else:
        return _fake_azure_ledger()
