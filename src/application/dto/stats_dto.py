from typing import Literal

from src.application.dto import BaseSchema
from src.application.dto.drug_catalog_dto import TaskStatus


StatsKind = Literal['all', 'central', 'total_catalogs', 'total_mappins']


class CentralCatalogStatsDto(BaseSchema):
    status: TaskStatus | None


class CatalogStatsDto(BaseSchema):
    total: int


class MappingsStatsDto(BaseSchema):
    total: int


class AdminStatsDto(BaseSchema):
    central_catalog: CentralCatalogStatsDto | None = None
    total_catalogs: CatalogStatsDto | None = None
    total_mappins: MappingsStatsDto | None = None
