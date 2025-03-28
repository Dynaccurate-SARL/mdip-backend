from enum import Enum
from ...lib.utils.helpers import BaseSchema
from ...lib.utils.helpers import docs_example
from ...lib.utils.helpers import MetaDatetimeSchema

from typing import Optional, List

from ..transaction.schemas import TransactionResponse


class EntityTypeEnum(str, Enum):
    BSG = 'BSG'
    WAT = 'WAT'
    PCA = 'PCA'
    MYC = 'MYC'


class EntityCreate(BaseSchema):
    entity_type: EntityTypeEnum
    origin: str
    destination: str
    size: float
    unit: str

    class Config:
        json_schema_extra = {
            "example": {
                'entity_type': 'BSG',
                'origin': 'Tank A',
                'destination': 'Tank B',
                'size': 300,
                'unit': 'L'
            }
        }


class EntityResponse(EntityCreate):
    id: int
    status: str
    transactions: Optional[List[TransactionResponse]] = []
    metadatetime: MetaDatetimeSchema

    class Config:
        json_schema_extra = {
            "example": {
                'entity_type': 'BSG',
                'origin': 'Tank A',
                'destination': 'Tank B',
                'size': 300,
                'unit': 'L',
                'status': 'Pending',
                'transactions': [TransactionResponse.Config.json_schema_extra['example']],
                "metadatetime": docs_example
            }
        }
