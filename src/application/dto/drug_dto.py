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
