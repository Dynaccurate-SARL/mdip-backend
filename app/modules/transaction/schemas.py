from ...lib.utils.helpers import BaseSchema

from enum import Enum
from datetime import datetime
from typing import Optional
from fastapi import UploadFile


class TransactionTypeEnum(Enum):
    STATUS_UPDATE = 'status_update'
    MATERIAL_COMPOSITION = 'material_composition'
    QUALITY_CONTROL = 'quality_control'
    LABORATORY_ANALYSIS = 'laboratory_analysis'
    SENSOR_RESULTS = 'sensor_results'


class TransactionStatus(Enum):
    READY = 'ready'
    COMMITING = 'commiting'


class TransactionCreate(BaseSchema):
    title: str
    category: TransactionTypeEnum
    summary: str | None = None
    file: UploadFile | None = None


class TransactionData(BaseSchema):
    title: str
    category: TransactionTypeEnum
    summary: str | None = None
    filename: str | None = None
    timestamp: datetime


class TransactionContentResponse(BaseSchema):
    title: str
    category: TransactionTypeEnum
    summary: str | None = None
    filename: str | None = None
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                'title': 'Set as processing',
                'category': 'status_update',
                'summary': 'Set as processing',
                'filename': 'example.pdf',
                'timestamp': datetime.now()
            }
        }


class TransactionResponse(BaseSchema):
    id: str | None = None
    status: TransactionStatus | None = None
    content: TransactionContentResponse | None = None

    class Config:
        json_schema_extra = {
            "example": {
                'id': '999.9',
                'status': 'ready',
                'content': TransactionContentResponse.Config.json_schema_extra['example']
            }
        }
