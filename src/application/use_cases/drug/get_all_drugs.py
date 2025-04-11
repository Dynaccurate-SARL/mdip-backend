from typing import List
from src.application.dto.drug_dto import DrugDto
from src.infrastructure.repositories.contract import DrugRepositoryInterface


class GetAllDrugsByDrugNameOrCodeUseCase:
    def __init__(self, drug_repository: DrugRepositoryInterface):
        self.drug_repository = drug_repository

    async def execute(self, drug_name_or_code: str) -> List[DrugDto]:
        drugs = await self.drug_repository.get_all_like_code_or_name(
            drug_name_or_code)
        return [DrugDto.model_validate(drug) for drug in drugs]
