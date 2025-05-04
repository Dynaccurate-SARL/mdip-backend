from src.application.dto.stats_dto import (
    AdminStatsDto, CentralCatalogStatsDto, CatalogStatsDto, 
    MappingsStatsDto, StatsKind)
from src.infrastructure.repositories.contract import (
    DrugCatalogRepositoryInterface, MappingRepositoryInterface)


class GetAdminStatsUseCase:
    def __init__(self, drug_catalog_repository: DrugCatalogRepositoryInterface,
                 mapping_repository: MappingRepositoryInterface):
        self.mapping_repository = mapping_repository
        self.drug_catalog_repository = drug_catalog_repository

    async def _get_catalogs_count(self) -> CatalogStatsDto:
        count = await self.drug_catalog_repository.get_total_count()
        return CatalogStatsDto(total=count)

    async def _get_central_catalog(self) -> CentralCatalogStatsDto:
        catalog = await self.drug_catalog_repository.get_central()
        status = catalog.status if catalog else None
        return CentralCatalogStatsDto(status=status)

    async def _get_mappings_count(self) -> MappingsStatsDto:
        count = await self.mapping_repository.get_total_count()
        return MappingsStatsDto(total=count)

    async def execute(self, kind: StatsKind) -> AdminStatsDto:
        # central catalog status only
        if kind == 'central':
            return AdminStatsDto(
                central_catalog=await self._get_central_catalog()
            )

        # catalogs count only
        if kind == 'total_catalogs':
            return AdminStatsDto(
                total_catalogs=await self._get_catalogs_count()
            )

        # mappins count only
        if kind == 'total_mappins':
            return AdminStatsDto(
                total_mappins=await self._get_mappings_count()
            )

        return AdminStatsDto(
            central_catalog=await self._get_central_catalog(),
            total_catalogs=await self._get_catalogs_count(),
            total_mappins=await self._get_mappings_count()
        )
