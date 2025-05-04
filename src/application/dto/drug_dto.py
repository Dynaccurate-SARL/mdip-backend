from pydantic import field_validator
from src.application.dto import BaseSchema


class DrugDto(BaseSchema):
    id: str
    catalog_id: str
    drug_code: str
    drug_name: str
    properties: dict

class DrugPaginatedDto(BaseSchema):
    data: list[DrugDto]
    page: int
    limit: int
    total: int


class DrugMappingsCount(BaseSchema):
    drug_name: str
    drug_code: str
    drug_id: str
    mapping_count: int

    @field_validator('drug_id', mode='before')
    def convert_timestamp_to_datetime(cls, value, values):
        if value is None:
            return None
        return str(value)