from logging import Logger, getLogger
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto import BaseSchema
from src.domain.entities.drug_mapping import DrugMapping
from src.infrastructure.repositories.idrug_repository import IDrugRepository
from src.infrastructure.repositories.imapping_repository import IMappingRepository
from src.infrastructure.services.pandas_parser.mapping.parse import DrugMappingParse


class MappingsTaskData(BaseSchema):
    mappings: List[DrugMappingParse]
    central_catalog_id: int
    related_catalog_id: int
    mapping_id: int


async def task(session: AsyncSession, data: MappingsTaskData,
               logger: Logger = getLogger(__name__)):
    def loginfo(msg: str): logger.info(f"{data.mapping_id} > {msg}")
    def logwarn(msg: str): logger.warning(f"{data.mapping_id} > {msg}")
    drug_repository = IDrugRepository(session)
    mapping_repository = IMappingRepository(session)

    loginfo(
        f"Mapping import task started, chunk size {len(data.mappings)}")
    central_drug_codes, related_drug_codes = [], []
    for mapping in data.mappings:
        central_drug_codes.append(mapping.drug_code)
        related_drug_codes.append(mapping.related_drug_code)

    loginfo("Creating a hash map with all central drug codes")
    central_drug_codes = await drug_repository.get_drug_map_by_catalog_id(
        data.central_catalog_id, central_drug_codes)

    loginfo("Creating a hash map with all related drug codes")
    related_drug_codes = await drug_repository.get_drug_map_by_catalog_id(
        data.related_catalog_id, related_drug_codes)

    loginfo("Importing mappins")
    for mapping in data.mappings:
        cid = central_drug_codes.get(mapping.drug_code)
        rid = related_drug_codes.get(mapping.related_drug_codes)
        if cid and rid:
            db_mapping = DrugMapping(
                mapping_id=data.mapping_id,
                drug_id=cid,
                related_drug_id=rid,
            )
            saved = await mapping_repository.save(db_mapping)

            log_message = ' '.join([
                f"Mapping between, central '{mapping.drug_code}' to",
                f"related '{mapping.related_drug_code}'",
                "created." if saved else "already exists."
            ])
            if saved:
                loginfo(log_message)
            else:
                logwarn(log_message)

    loginfo("Mapping chunk import completed")
