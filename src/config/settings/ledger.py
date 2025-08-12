from pydantic import model_validator

from src.config.settings.base import BaseEnvs


class LedgerEnvs:
    AZURE_LEDGER_URL: str | None = None
    AZURE_LEDGER_CERTIFICATE_PATH: str | None = None
    AZURE_CREDENTIAL_TENNANT_ID: str | None = None
    AZURE_CREDENTIAL_CLIENT_ID: str | None = None
    AZURE_CREDENTIAL_CERTIFICATE_PATH: str | None = None

    @model_validator(mode="after")
    def check_upload_strategy(cls, values: "BaseEnvs") -> "LedgerEnvs":
        environment = values.ENVIRONMENT

        if environment == "PROD":
            required = [
                "AZURE_LEDGER_URL",
                "AZURE_LEDGER_CERTIFICATE_PATH",
                "AZURE_CREDENTIAL_TENNANT_ID",
                "AZURE_CREDENTIAL_CLIENT_ID",
                "AZURE_CREDENTIAL_CERTIFICATE_PATH"
            ]
            for field in required:
                if not getattr(values, field):
                    raise ValueError(
                        f"'{field}' is required when 'ENVIRONMENT' is 'PROD'\n"
                    )
        return values
