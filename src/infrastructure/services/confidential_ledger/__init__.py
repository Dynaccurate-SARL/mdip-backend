
import os
from uuid import uuid4
from unittest.mock import Mock

from src.infrastructure.services.confidential_ledger.azure_ledger import AzureLedger, TransactionInserted


def fake_azure_ledger():
    fake = Mock(spec=AzureLedger)
    fake.insert_transaction.return_value = TransactionInserted(
        status='processing',
        transaction_id=str(uuid4()),
    )
    fake.retrieve_transaction.return_value = TransactionInserted(
        status='ready',
        transaction_id=str(uuid4()),
        transaction_data={'data': 'fake_data'}
    )
    return fake


class ConfidentialLedgerService:
    def __init__(
            self, azure_ledger_url: str, azure_ledger_certificate_path: str):
        if os.getenv('ENVIRONMENT', None) == 'PROD':
            self.confidential_ledger: AzureLedger = AzureLedger(
                azure_ledger_url, azure_ledger_certificate_path)
        else:
            self.confidential_ledger: AzureLedger = fake_azure_ledger()
