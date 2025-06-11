from taskiq_aio_pika import AioPikaBroker
from taskiq_dependencies import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_config
from src.infrastructure.db.engine import get_session
from src.infrastructure.taskiq.catalog_import import (
    ParseTaskData, task as catalog_import)
from src.infrastructure.taskiq.mapping_import import (
    MappingsTaskData, task as mapping_import)


broker = AioPikaBroker(get_config().RABBITMQ_URL, qos=4)


@broker.task
async def catalog_import_taskiq(
        data: dict, session: AsyncSession = Depends(get_session)):
    data: ParseTaskData = ParseTaskData.model_validate(data)
    await catalog_import(session, data, get_config())


@broker.task
async def mapping_import_taskiq(
        data: dict, session: AsyncSession = Depends(get_session)):
    data: MappingsTaskData = MappingsTaskData.model_validate(data)
    await mapping_import(session, data)
