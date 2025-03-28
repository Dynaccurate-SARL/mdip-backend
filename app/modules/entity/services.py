from datetime import datetime
import json
from typing import List

from app.config import get_config
from app.db.repositories.models import Transaction
from app.lib.utils.helpers import serialize_datetime

from ...lib.utils.exceptions import ResourseNotFound
from ...lib.confidential_ledger import ledger_service_builder

from ...lib.utils.enums import ErrorCodes

from ...db.repositories import EntityRepository
from ...db.repositories.models import Entity, EntityStatus
from .schemas import EntityCreate, EntityTypeEnum
from .schemas import EntityResponse
from ..transaction.schemas import TransactionData, TransactionResponse, TransactionTypeEnum
from ..transaction.schemas import TransactionStatus
from ..transaction.schemas import TransactionContentResponse

ledger = ledger_service_builder()


class EntityService:

    async def create(self, entity: EntityCreate) -> EntityResponse:
        """
        Creates an entity.

        Args:
            entity (EntityCreate): The entity creation model.

        Returns:
            EntityResponse: The entity response model.
        """

        entity_create = Entity(**entity.model_dump())
        entity_created = await entity_create.insert()

        transaction_data = TransactionData(
            title='Set as Pending',
            category=TransactionTypeEnum.STATUS_UPDATE.value,
            timestamp=datetime.now()
        )

        entry = ledger.insert_transaction(transaction_data)

        content = json.dumps(entry.contents, default=serialize_datetime) if get_config().LEDGER_TYPE == 'db' else ''
        transaction_create = Transaction(
            _entity_id=entity_created.id,
            id=entry.transactionId,
            content=content
        )
        transaction_created = await transaction_create.insert()

        response = EntityResponse.model_validate(entity_created)
        response.transactions.append(TransactionResponse(id=transaction_created.id,
                                                         status=TransactionStatus.COMMITING,
                                                         content=TransactionContentResponse(**entry.contents)))

        return response
    
    async def update_status(self, id: int) -> EntityResponse:
        """
        Updates entity status.

        Args:
            id (int): Entity id.

        Returns:
            EntityResponse: The entity response model.
        """

        entity = await EntityRepository.get_by_id(id)
        if entity == None:
            raise ResourseNotFound(message='Entity not found.',
                                   reason=ErrorCodes.NOT_FOUND)
        
        if entity.status != EntityStatus.DONE:
            if entity.status == EntityStatus.PENDING:
                entity.status = EntityStatus.PROCESSING
            else:
                entity.status = EntityStatus.DONE

            await entity.update(status=entity.status)

            transaction_data = TransactionData(
                title=f'Set as {entity.status.value.lower()}',
                category=TransactionTypeEnum.STATUS_UPDATE.value,
                timestamp=datetime.now()
            )

            entry = ledger.insert_transaction(transaction_data)

            content = json.dumps(entry.contents, default=serialize_datetime) if get_config().LEDGER_TYPE == 'db' else ''
            transaction_create = Transaction(
                _entity_id=entity.id,
                id=entry.transactionId,
                content=content
            )
            transaction_created = await transaction_create.insert()
            entity.reg_transactions.append(transaction_created)

        entity_response = EntityResponse.model_validate(entity)
        entity_response.transactions = []

        for transaction in entity.reg_transactions:
            entry = ledger.retrieve_transaction(transaction)
            entity_response.transactions.append(
                TransactionResponse(id=transaction.id,
                                    status=TransactionStatus.READY,
                                    content=TransactionContentResponse(**entry.contents)))

        return entity_response


    async def delete_by_id(self, id: int) -> EntityResponse:
        """
        Deletes an entity.

        Args:
            id (int): The entity ID.

        Returns:
            EntityResponse: The entity response model.
        """
        entity = await EntityRepository.get_by_id(id)
        if entity == None:
            raise ResourseNotFound(message='Entity not found.',
                                   reason=ErrorCodes.NOT_FOUND)

        await entity.update(is_active=False)
        return EntityResponse.model_validate(entity)

    async def get_by_id(self, id: int) -> EntityResponse:
        """
        Returns an entity.

        Args:
            id (int): The entity ID.

        Returns:
            EntityResponse: The entity response model.
        """

        entity = await EntityRepository.get_by_id(id)
        if entity == None:
            raise ResourseNotFound(message='Entity not found.',
                                   reason=ErrorCodes.NOT_FOUND)
        entity_response = EntityResponse.model_validate(entity)
        entity_response.transactions = []

        for transaction in entity.reg_transactions:
            entry = ledger.retrieve_transaction(transaction)
            entity_response.transactions.append(
                TransactionResponse(id=transaction.id,
                                    status=TransactionStatus.READY,
                                    content=TransactionContentResponse(**entry.contents)))

        return entity_response

    async def get_all(self, entity_type: EntityTypeEnum,  name: str) -> List[EntityResponse]:
        """
        Returns all entities.

        Args:
            name (str): Drug name to filter.

        Returns:
            DrugsResponse: The entity response model.
        """

        entities = await EntityRepository.get_by_type_and_name(entity_type, name)

        return [EntityResponse.model_validate(entity) for entity in entities]
