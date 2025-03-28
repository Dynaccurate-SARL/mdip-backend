import json
import uuid
import logging

from datetime import datetime

from ...config import get_config

from ...lib.utils.exceptions import ResourseNotFound
from ...lib.utils.enums import ErrorCodes
from ...lib.utils.helpers import serialize_datetime
from ...lib.confidential_ledger import ledger_service_builder
from ...lib.file_service import upload_file, download_file

from ...db.repositories import EntityRepository
from ...db.repositories import TransactionRepository
from ...db.repositories.models import Transaction

from .schemas import TransactionCreate, TransactionData
from .schemas import TransactionResponse
from .schemas import TransactionContentResponse
from .schemas import TransactionTypeEnum
from .schemas import TransactionStatus
from fastapi.responses import FileResponse, HTMLResponse


ledger = ledger_service_builder()


class TransactionService:
    async def create(self, entity_id: int, transaction: TransactionCreate) -> TransactionResponse:
        """
        Creates a transaction.

        Args:
            transaction (TransactionCreate): The transaction creation model.

        Returns:
            TransactionResponse: The transaction response model.
        """

        entity = await EntityRepository.get_by_id(entity_id)
        if entity == None:
            raise ResourseNotFound(message='Entity not found.',
                                   reason=ErrorCodes.ENTITY_NOT_FOUND)

        transaction_data = TransactionData(
            title=transaction.title,
            category=transaction.category,
            summary=transaction.summary,
            filename=f'{str(uuid.uuid4())}_{transaction.file.filename}' if transaction.file else None,
            timestamp=datetime.now()
        )

        if transaction.file:
            upload_file(transaction_data.filename, transaction.file.file)

        entry = ledger.insert_transaction(transaction_data)

        transaction_entry = {
            '_entity_id': entity_id,
            'id': entry.transactionId,
            'content': json.dumps(entry.contents, default=serialize_datetime) if get_config().LEDGER_TYPE == 'db' else ''
        }

        transaction_create = Transaction(**transaction_entry)
        transaction_created = await transaction_create.insert()

        return TransactionResponse(
            id=transaction_created.id,
            status=TransactionStatus.COMMITING,
            content=TransactionContentResponse(
                title=entry.contents['title'],
                category=entry.contents['category'],
                summary=entry.contents.get('summary', None),
                filename=entry.contents.get('filename', None),
                timestamp=entry.contents['timestamp']
            )
        )

    async def get_by_id(self, id: str) -> TransactionResponse:
        """
        Returns a transaction.

        Args:
            id (int): The transaction ID.

        Returns:
            TransactionResponse: The transaction response model.
        """

        transaction = await TransactionRepository.get_by_id(id)
        if transaction == None:
            raise ResourseNotFound(message='Transaction not found.',
                                   reason=ErrorCodes.NOT_FOUND)
        entry = ledger.retrieve_transaction(transaction)

        return TransactionResponse(
            id=entry.transactionId,
            status=TransactionStatus.READY,
            content=TransactionContentResponse(
                title=entry.contents['title'],
                category=entry.contents['category'],
                summary=entry.contents.get('summary', None),
                filename=entry.contents.get('filename', None),
                timestamp=entry.contents['timestamp']
            )
        )

    async def download_file(self, id) -> FileResponse:
        """
        Returns a transaction attacjed file.

        Args:
            id (int): The transaction ID.

        Returns:
            FileResponse: The attached file.
        """
        transaction = await TransactionRepository.get_by_id(id)
        if transaction == None:
            raise ResourseNotFound(message='Transaction not found.',
                                   reason=ErrorCodes.NOT_FOUND)
        entry = ledger.retrieve_transaction(transaction)
        
        if filename := entry.contents.get('filename', None):
            file_path = download_file(filename)
            return FileResponse(file_path, filename=filename, status_code=200)
        return HTMLResponse(status_code=200)