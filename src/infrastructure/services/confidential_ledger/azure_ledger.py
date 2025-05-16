import os
import json
from typing import Dict, Literal, TypedDict
from azure.identity import DefaultAzureCredential
from azure.confidentialledger import ConfidentialLedgerClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.exceptions import HttpResponseError

from src.application.dto import BaseSchema
from src.utils.checksum import dict_hash


# def _created_at() -> str:
#     if os.getenv('ENVIRONMENT', None) == 'TEST':
#         date = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
#         return date.isoformat()
#     return datetime.now(timezone.utc).isoformat()


class LedgerEntry(TypedDict):
    transactionId: str
    contents: str


class TransactionInserted(BaseSchema):
    transaction_id: str
    status: Literal['ready', 'processing']
    transaction_data: Dict | None = None


class AzureLedger:
    def __init__(self, ledger_url: str, certificate_path: str):
        credential = DefaultAzureCredential()
        ledger_client = ConfidentialLedgerClient(
            endpoint=ledger_url,
            credential=credential,
            ledger_certificate_path=certificate_path
        )
        self.ledger_client = ledger_client

    def insert_transaction(self, data: Dict):
        sample_entry = {
            "contents": {
                "data": json.dumps(data),
                'hash': dict_hash(data)
            }
        }

        self.ledger_client.create_ledger_entry(entry=sample_entry)
        latest_entry: LedgerEntry = self.ledger_client.\
            get_current_ledger_entry()
        transaction_id = latest_entry['transactionId']

        return TransactionInserted(
            status='processing',
            transaction_id=transaction_id,
        )

    def retrieve_transaction(self, transaction_id: str):
        try:
            poller = self.ledger_client.begin_get_ledger_entry(transaction_id)
            entry = poller.result()

            data = TransactionInserted(
                transaction_id=transaction_id, status='processing')
            if (entry["state"] == 'Ready'):
                data.transaction_data = json.loads(entry['entry']['contents'])
            return data
        except ResourceNotFoundError:
            return None
        except HttpResponseError:
            return None
