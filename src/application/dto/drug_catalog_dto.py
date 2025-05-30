from typing import Literal

from src.application.dto import BaseSchema


TaskStatus = Literal["created", "processing", "completed", "failed"]
_CountryCode = Literal[
    "AT",
    "BE",
    "CA",
    "CY",
    "CZ",
    "DK",
    "EE",
    "ES",
    "EU",
    "FI",
    "FR",
    "GR",
    "HR",
    "HU",
    "IE",
    "LU",
    "LV",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SE",
    "SK",
    "UK",
    "US",
]
_OtherCode = Literal["XX", "EU"]
CountryCode = _OtherCode | _CountryCode


class DrugCatalogCreateDto(BaseSchema):
    name: str
    country: CountryCode
    version: str
    notes: str
    is_central: bool


class DrugCatalogCreatedDto(BaseSchema):
    id: str
    name: str
    country: CountryCode
    version: str
    notes: str
    is_central: bool
    status: TaskStatus


class DrugCatalogDto(BaseSchema):
    id: str
    name: str
    country: CountryCode
    version: str
    notes: str
    is_central: bool
    status: TaskStatus


class DrugCatalogPaginatedDto(BaseSchema):
    data: list[DrugCatalogDto]
    page: int
    limit: int
    total: int
