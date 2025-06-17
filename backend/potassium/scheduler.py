from loguru import logger

from potassium.debezium.client import KafkaConnectClient
from potassium.debezium.exceptions import ConnectorFailedStateError
from potassium.debezium.models import FullConnectorStatus


@logger.catch()
async def check_connector_statuses_job(restart_connectors: bool) -> None:
    logger.info("APScheduler job: Checking connector statuses...")
    client = KafkaConnectClient()
    connectors = await client.list_connectors()
    logger.info(f"Successfully listed connectors: {connectors}")

    errors: list[Exception] = []

    for connector in connectors:
        logger.info("------------------------------------------------------------------------")
        config = await client.get_connector_config(connector)
        logger.info(f"Successfully parsed config for {connector}: {config.model_dump_json(by_alias=True, indent=2)}")

        connector_status: FullConnectorStatus = await client.get_connector_status(connector)
        logger.info(f"Successfully parsed status for {connector}: {connector_status.model_dump_json(indent=2)}")

        if any(task.state == "FAILED" for task in connector_status.tasks):
            if restart_connectors:
                await client.restart_connectors(connector)

            errors.append(
                ConnectorFailedStateError(
                    connector=connector, task_errors=connector_status.task_errors, restart_connectors=restart_connectors
                )
            )

    if errors:
        for error in errors:
            logger.error(str(error))
