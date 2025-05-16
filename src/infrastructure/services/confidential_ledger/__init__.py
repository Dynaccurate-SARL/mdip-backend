
import os
from uuid import uuid4
from unittest.mock import Mock

from src.infrastructure.services.confidential_ledger.azure_ledger import AzureLedger
from src.infrastructure.services.confidential_ledger.contract import (
    LedgerInterface, TransactionInserted)


def fake_azure_ledger():
    fake = Mock(spec=LedgerInterface)
    fake.insert_transaction.return_value = TransactionInserted(
        status='processing',
        transaction_id=uuid4(),
    )
    fake.retrieve_transaction.return_value = TransactionInserted(
        status='ready',
        transaction_id=uuid4(),
        transaction_data={'data': 'fake_data'}
    )
    return fake


def ledger_builder(azure_ledger_url: str, 
                   azure_ledger_certificate_path: str) -> LedgerInterface:
    if os.getenv('ENVIRONMENT', None) == 'PROD':
        return AzureLedger(
            azure_ledger_url, azure_ledger_certificate_path)
    else:
        return fake_azure_ledger()
