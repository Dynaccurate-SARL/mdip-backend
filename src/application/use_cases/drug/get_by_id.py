from src.application.dto.drug_dto import DrugDto
from src.infrastructure.repositories.contract import (
    DrugRepositoryInterface, MappingRepositoryInterface)


class GetDrugByIdUseCase:
    def __init__(self, drug_repository: DrugRepositoryInterface,
                 mapping_repository: MappingRepositoryInterface):
        self.drug_repository = drug_repository
        self.mapping_repository = mapping_repository

    async def execute(self, drug_id: int) -> DrugDto | None:
        drug = await self.drug_repository.get_by_id(drug_id)
        if drug:
            mapping_parents = await self.mapping_repository.\
                get_drugs_id_by_related_to(drug._id)

            result = DrugDto.model_validate(drug)
            result.mapping_parents = [str(id) for id in mapping_parents]
            return result
