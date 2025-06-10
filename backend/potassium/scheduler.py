from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from potassium.debezium.client import KafkaConnectClient
from potassium.debezium.models import FullConnectorStatus

scheduler = AsyncIOScheduler()


def get_scheduler():
    return scheduler


async def check_connector_statuses_job():
    logger.info("APScheduler job: Checking connector statuses...")
    client = KafkaConnectClient()
    connectors = await client.list_connectors()
    logger.info(f"Successfully listed connectors: {connectors}")

    for connector in connectors:
        logger.info("------------------------------------------------------------------------")
        config = await client.get_connector_config(connector)
        logger.info(f"Successfully parsed config for {connector}: {config.model_dump_json(by_alias=True, indent=2)}")

        status: FullConnectorStatus = await client.get_connector_status(connector)
        logger.info(f"Successfully parsed status for {connector}: {status.model_dump_json(indent=2)}")

        if any(task.state == "FAILED" for task in status.tasks):
            logger.info(f"Restarting {connector}!")
            await client.restart_connectors(connector)
