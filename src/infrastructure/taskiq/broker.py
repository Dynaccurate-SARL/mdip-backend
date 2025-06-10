from taskiq_aio_pika import AioPikaBroker

from src.config.settings import get_config
from src.infrastructure.taskiq.catalog_import import task as import_catalog


broker = AioPikaBroker(get_config().RABBITMQ_URL)


@broker.task
async def catalog_import_task(data: dict):
    await import_catalog(data)
