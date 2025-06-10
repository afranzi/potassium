from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from potassium.debezium.client import KafkaConnectClient
from potassium.debezium.exceptions import ConnectorFailedStateError
from potassium.debezium.models import FullConnectorStatus

scheduler = AsyncIOScheduler()


def get_scheduler():
    return scheduler


@logger.catch()
async def check_connector_statuses_job(restart_connectors: bool) -> None:
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
            if restart_connectors:
                logger.error(f"Connector {connector} is in FAILED state, proceeding to restart it programmatically.")
                await client.restart_connectors(connector)
            else:
                raise ConnectorFailedStateError(connector=connector)
