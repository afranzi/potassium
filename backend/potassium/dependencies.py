from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import HTTPException, Request, status
from loguru import logger

from potassium.debezium.client import KafkaConnectClient
from potassium.kafka.client import KafkaClient


def get_kafka_client(request: Request) -> KafkaClient:
    if not hasattr(request.app.state, "kafka_producer") or request.app.state.kafka_producer is None:
        logger.critical("KafkaClient not found in app.state. Was it created during startup?")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Kafka service not available")
    return request.app.state.kafka_producer


def get_scheduler(request: Request) -> AsyncIOScheduler:
    if not hasattr(request.app.state, "scheduler") or request.app.state.scheduler is None:
        logger.critical("Scheduler not found in app.state. Was it created during startup?")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Scheduler service not available")
    return request.app.state.scheduler


def get_kafka_connect_client(request: Request) -> KafkaConnectClient:
    if not hasattr(request.app.state, "kafka_connect") or request.app.state.kafka_connect is None:
        logger.critical("KafkaConnect not found in app.state. Was it created during startup?")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="KafkaConnect service not available"
        )
    return request.app.state.kafka_connect
