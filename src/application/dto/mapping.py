from typing import List, Dict
from src.application.dto import BaseSchema
from src.application.dto.drug_catalog_dto import CountryCode


class BaseDrugDto(BaseSchema):
    id: str
    drug_name: str
    drug_code: str
    properties: Dict


class MappingDrugDto(BaseDrugDto):
    country: CountryCode


class CentralDrugMappingDto(BaseSchema):
    drug: BaseDrugDto
    mappings: List[MappingDrugDto]
