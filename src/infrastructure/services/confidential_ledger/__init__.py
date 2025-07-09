from typing import Literal

from src.infrastructure.services.confidential_ledger.contract import LedgerInterface
from src.infrastructure.services.confidential_ledger.iazure_ledger import AzureLedger
from src.infrastructure.services.confidential_ledger.ifake_json_ledger import (
    FakeJsonLedger,
)


def ledger_builder(
    azure_ledger_url: str,
    azure_credentials_certificate_path: str,
    azure_ledger_certificate_path: str,
    environment: Literal["PROD", "DEV"] = "DEV"
) -> LedgerInterface:
    if environment == "PROD":
        return AzureLedger(
            azure_ledger_url, 
            azure_credentials_certificate_path, 
            azure_ledger_certificate_path
        )
    else:
        return FakeJsonLedger()
