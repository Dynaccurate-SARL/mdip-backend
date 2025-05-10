from typing import Literal
from fastapi import UploadFile

from src.application.dto import BaseSchema


CountryCode = Literal[
    'CA', 'EU', 'FR', 'US', 'UK', 'SE',
    'RO', 'PL', 'LV', 'IE', 'ES', 'BE'
]

Status = Literal['created', 'processing', 'completed', 'failed']


class DrugCatalogCreateDto(BaseSchema):
    name: str
    country: CountryCode
    version: str
    notes: str
    is_central: bool
    file: UploadFile


class DrugCatalogCreatedDto(BaseSchema):
    id: str
    name: str
    country: CountryCode
    version: str
    notes: str
    is_central: bool
    status: Status
    transaction_id: str = ''


class DrugCatalogDto(BaseSchema):
    id: str
    name: str
    country: CountryCode
    version: str
    notes: str
    is_central: bool
    status: Status


class DrugCatalogPaginatedDto(BaseSchema):
    data: list[DrugCatalogDto]
    page: int
    limit: int
    total: int
