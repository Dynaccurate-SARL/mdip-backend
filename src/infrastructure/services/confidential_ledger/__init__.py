
import os

from src.infrastructure.services.confidential_ledger.azure_ledger import AzureLedger
from src.infrastructure.services.confidential_ledger.contract import (
    LedgerInterface)
from src.infrastructure.services.confidential_ledger.fake_json_ledger import FakeJsonLedger




def ledger_builder(azure_ledger_url: str, 
                   azure_ledger_certificate_path: str) -> LedgerInterface:
    if os.getenv('ENVIRONMENT', None) == 'PROD':
        return AzureLedger(
            azure_ledger_url, azure_ledger_certificate_path)
    else:
        return FakeJsonLedger()
