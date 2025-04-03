from typing import Literal
from pydantic import model_validator

LedgerStrategy = Literal['DB', 'AZURE']


class LedgerEnvs:
    LEDGER_STRATEGY: LedgerStrategy
    # strategy: azure
    AZURE_LEDGER_URL: str | None = None
    AZURE_CERTIFICATE_PATH: str | None = None

    @model_validator(mode='after')
    def check_upload_strategy(cls, values: 'LedgerEnvs') -> 'LedgerEnvs':
        strategy = values.LEDGER_STRATEGY

        if strategy == "AZURE":
            required = ["AZURE_LEDGER_URL", "AZURE_CERTIFICATE_PATH"]
            for field in required:
                if not getattr(values, field):
                    raise ValueError(
                        f"'{field}' is required when 'LEDGER_STRATEGY' is 'AZURE'\n")
        return values
