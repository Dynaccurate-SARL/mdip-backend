from typing import Literal

from src.application.dto import BaseSchema
from src.domain.entities.drug_catalog import ImportStatus


StatsKind = Literal['all', 'central', 'total_catalogs', 'total_mappins']


class CentralCatalogStatsDto(BaseSchema):
    status: ImportStatus | None


class CatalogStatsDto(BaseSchema):
    total: int


class MappingsStatsDto(BaseSchema):
    total: int


class AdminStatsDto(BaseSchema):
    central_catalog: CentralCatalogStatsDto | None = None
    total_catalogs: CatalogStatsDto | None = None
    total_mappins: MappingsStatsDto | None = None
