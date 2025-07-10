from typing import Literal

from src.infrastructure.services.confidential_ledger.contract import LedgerInterface
from src.infrastructure.services.confidential_ledger.iazure_ledger import AzureLedger
from src.infrastructure.services.confidential_ledger.ifake_json_ledger import (
    FakeJsonLedger,
)


def ledger_builder(
    azure_ledger_url: str,
    azure_ledger_certificate_path: str,
    azure_credentials_tenant_id: str,
    azure_credentials_client_id: str,
    azure_credentials_certificate_path: str,
    environment: Literal["PROD", "DEV"] = "DEV"
) -> LedgerInterface:
    if environment == "PROD":
        return AzureLedger(
            azure_ledger_url,
            azure_ledger_certificate_path,
            azure_credentials_tenant_id,
            azure_credentials_client_id,
            azure_credentials_certificate_path
        )
    else:
        return FakeJsonLedger()
