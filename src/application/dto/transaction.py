from typing import Literal

from src.application.dto import BaseSchema
from src.application.dto.drug_catalog_dto import TaskStatus


class BaseTransactionDto(BaseSchema):
    transaction_id: str
    # Transaction data is stored in JSON string format
    status: TaskStatus
    filename: str
    file_checksum: str
    created_at: str
    created_at_tz: Literal["UTC"]


class CatalogTransactionDto(BaseTransactionDto):
    catalog_id: str


class MappingTransactionDto(BaseTransactionDto):
    mapping_id: str
    catalog_id: str
    related_catalog_id: str


class TransactionDto(BaseSchema):
    valid: bool
