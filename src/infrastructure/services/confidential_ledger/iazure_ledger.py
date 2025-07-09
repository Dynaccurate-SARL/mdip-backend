import json
from typing import Dict, TypedDict
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError
from azure.confidentialledger import ConfidentialLedgerClient

from src.utils.checksum import dict_hash
from src.infrastructure.services.confidential_ledger.contract import (
    LedgerInterface,
    TransactionInserted,
)


class LedgerEntry(TypedDict):
    transactionId: str
    contents: str


class AzureLedger(LedgerInterface):
    def __init__(self, ledger_url: str, certificate_path: str):
        credential = DefaultAzureCredential()
        ledger_client = ConfidentialLedgerClient(
            endpoint=ledger_url,
            credential=credential,
            ledger_certificate_path=certificate_path,
        )
        self.ledger_client = ledger_client

    def insert_transaction(self, data: Dict):
        sample_entry = {"contents": json.dumps({
            "data": data, "hash": dict_hash(data)
        })}
        print(f"Inserting transaction with data: \n {sample_entry}")

        self.ledger_client.create_ledger_entry(entry=sample_entry)
        latest_entry: LedgerEntry = self.ledger_client.get_current_ledger_entry()
        transaction_id = latest_entry["transactionId"]

        return TransactionInserted(
            status="processing",
            transaction_id=transaction_id,
        )

    def retrieve_transaction(self, transaction_id: str):
        try:
            poller = self.ledger_client.begin_get_ledger_entry(
                str(transaction_id))
            entry = poller.result()

            data = TransactionInserted(
                transaction_id=transaction_id, status="processing"
            )
            if entry["state"] == "Ready":
                data.status = "ready"
                data.transaction_data = json.loads(entry["entry"]["contents"])
            return data
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None
