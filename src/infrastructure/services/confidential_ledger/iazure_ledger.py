import json
from typing import TypedDict
from azure.identity import DefaultAzureCredential
from azure.confidentialledger import ConfidentialLedgerClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.exceptions import HttpResponseError
from src.domain.entities.ledger_transaction import LedgerTransaction
from src.infrastructure.repositories.contract import LedgerTransactionRepositoryInterface
from src.infrastructure.services.confidential_ledger.contract import (
    Ledger,
    TransactionData,
    TransactionInserted)


class LedgerEntry(TypedDict):
    transactionId: str
    contents: str


class AzureLedger(Ledger):
    def __init__(self, ledger_url: str, certificate_path: str,
                 lt_repository: LedgerTransactionRepositoryInterface):
        credential = DefaultAzureCredential()
        ledger_client = ConfidentialLedgerClient(
            endpoint=ledger_url,
            credential=credential,
            ledger_certificate_path=certificate_path
        )
        self.ledger_client = ledger_client
        self.lt_repository = lt_repository

    async def insert_transaction(self, data: TransactionData):
        sample_entry = {"contents": json.dumps(
            data.model_dump(exclude_none=True))}

        self.ledger_client.create_ledger_entry(entry=sample_entry)
        latest_entry: LedgerEntry = self.ledger_client.get_current_ledger_entry()
        transaction_id = latest_entry['transactionId']

        ltransaction = LedgerTransaction(
            transaction_id=transaction_id,
            entity_name=data.entity_name,
            entity_id=data.entity_id,
        )
        ltransaction = await self.lt_repository.save(ltransaction)

        return TransactionInserted(
            status='processing',
            transaction_id=transaction_id,
            content=json.loads(latest_entry['contents'])
        )

    async def retrieve_transaction(self, transaction_id: str):
        try:
            poller = self.ledger_client.begin_get_ledger_entry(transaction_id)
            entry = poller.result()

            data = TransactionInserted(status='processing')
            if (entry["state"] == 'Ready'):
                data.transaction_id = transaction_id
                data.content = json.loads(entry['entry']['contents'])
            return data
        except ResourceNotFoundError:
            return None
        except HttpResponseError as e:
            return None
