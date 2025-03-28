import json
import uuid

from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.confidentialledger import ConfidentialLedgerClient

from app.config import get_config

from app.lib.utils.exceptions import ResourceNotReady
from app.lib.utils.exceptions import ResourseNotFound
from app.lib.utils.exceptions import BadRequest
from app.lib.utils.enums import ErrorCodes
from azure.core.exceptions import ResourceNotFoundError
from azure.core.exceptions import HttpResponseError

from ..modules.transaction.schemas import TransactionData

from ..db.repositories.models.Transaction import Transaction

from app.lib.utils.helpers import serialize_datetime


def ledger_service_builder():
    if get_config().LEDGER_TYPE == 'confidential_ledger':
        return ConfidentialLedgerService()
    else:
        return DBLedgerService()
    

class TransactionInserted(BaseModel):
    contents: dict
    transactionId: str


class DBLedgerService():
    def insert_transaction(self, data: TransactionData) -> TransactionInserted:
        return TransactionInserted(contents=data.model_dump(exclude_none=True), transactionId=str(uuid.uuid4()))

    def retrieve_transaction(self, transaction: Transaction) -> TransactionInserted:
        return TransactionInserted(contents=json.loads(transaction.content), transactionId=transaction.id)


class ConfidentialLedgerService():
    def __start_client(self) -> ConfidentialLedgerClient:
        credential = DefaultAzureCredential()
        ledger_client = ConfidentialLedgerClient(
            endpoint=get_config().LEDGER_URL,
            credential=credential,
            ledger_certificate_path=get_config().CERTIFICATE_FILE
        )
        return ledger_client

    def insert_transaction(self, data: TransactionData) -> TransactionInserted:
        client = self.__start_client()

        sample_entry = {"contents": json.dumps(
            data.model_dump(exclude_none=True), default=serialize_datetime)}

        client.create_ledger_entry(entry=sample_entry)
        latest_entry = client.get_current_ledger_entry()
        
        return TransactionInserted(
            contents=json.loads(latest_entry['contents']), 
            transactionId=latest_entry['transactionId']
        )

    def retrieve_transaction(self, transaction: Transaction) -> TransactionInserted:
        client = self.__start_client()
        try:
            poller = client.begin_get_ledger_entry(
                transaction_id=transaction.id.strip())
            entry = poller.result()

            if (entry["state"] != 'Ready'):
                raise ResourceNotReady(message=f'Transaction {transaction} is still being processed...',
                                       reason=ErrorCodes.RESOURCE_STILL_PROCESSING)

            return TransactionInserted(
                contents=json.loads(entry['entry']['contents']), 
                transactionId=entry['entry']['transactionId']
            )

        except ResourceNotFoundError:
            raise ResourseNotFound(message=f'Transaction {transaction} does not exist...',
                                   reason=ErrorCodes.NOT_FOUND)
        except HttpResponseError as e:
            raise BadRequest(message=e.message,
                             reason=ErrorCodes.LEDGER_ERROR)
