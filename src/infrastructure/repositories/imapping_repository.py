from src.domain.entities.drug_mapping import DrugMapping
from src.infrastructure.repositories.contract import MappingRepositoryInterface


class IMappingRepository(MappingRepositoryInterface):

    async def save(self, mapping: DrugMapping) -> DrugMapping:
        self.session.add(mapping)
        await self.session.commit()
        await self.session.refresh(mapping)
        return mapping
