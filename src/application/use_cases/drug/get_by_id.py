from src.application.dto.drug_dto import DrugDto
from src.infrastructure.repositories.contract import DrugRepositoryInterface


class GetDrugByIdUseCase:
    def __init__(self, drug_repository: DrugRepositoryInterface):
        self.drug_repository = drug_repository

    async def execute(self, drug_id: int) -> DrugDto | None:
        drug = await self.drug_repository.get_by_id(drug_id)
        if drug:
            return DrugDto.model_validate(drug)
