from typing import Literal
from fastapi import UploadFile

from src.application.dto import BaseSchema


CountryCode = Literal[
    "AF", "AL", "DZ", "AD", "AO", "AR", "AM", "AU", "AT", "AZ", "BH",
    "BD", "BY", "BE", "BZ", "BJ", "BO", "BA", "BR", "BG", "CA", "CL",
    "CN", "CO", "HR", "CU", "CY", "CZ", "DK", "EG", "EE", "FI", "FR",
    "DE", "GR", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IL", "IT",
    "JP", "JO", "KZ", "KE", "KW", "LV", "LB", "LY", "LT", "LU", "MG",
    "MY", "MX", "MC", "MA", "NL", "NZ", "NG", "KP", "NO", "OM", "PK",
    "PA", "PE", "PH", "PL", "PT", "QA", "RO", "RU", "SA", "SN", "RS",
    "SG", "SK", "SI", "ZA", "KR", "ES", "SE", "CH", "TH", "TN", "TR",
    "UA", "AE", "GB", "US", "UY", "VE", "VN", "YE", "ZW"
]

class DrugCatalogCreateDto(BaseSchema):
    name: str
    country: CountryCode
    version: str
    notes: str
    file: UploadFile

class DrugCatalogCreatedDto(BaseSchema):
    id: int
    name: str
    country: CountryCode
    version: str
    notes: str
    transaction_id: str = ''