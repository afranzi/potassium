from contextlib import asynccontextmanager
from typing import AsyncGenerator

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from loguru import logger

from potassium.api.router import api_router
from potassium.config.settings import settings
from potassium.debezium.client import KafkaConnectClient
from potassium.kafka.client import KafkaClient, KafkaSettings
from potassium.scheduler import check_connector_statuses_job
from potassium.utils.logs import init_logs


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    init_logs(verbose=settings.debug, app_name=settings.app_name, slack_secret=settings.slack_secret)

    logger.info("Starting up Potassium API...")

    logger.info("Starting up Kafka clients...")
    kafka_settings = KafkaSettings(secret_name=settings.kafka_secret)
    app.state.kafka_client = KafkaClient(settings=kafka_settings)
    app.state.kafka_connect_client = KafkaConnectClient()

    # Conditionally start the scheduler and add the job
    if settings.job_enabled:
        logger.info("Setting up scheduler check...")
        scheduler = AsyncIOScheduler()
        app.state.scheduler = scheduler

        scheduler.add_job(
            check_connector_statuses_job,
            "interval",
            seconds=settings.job_frequency_seconds,
            id="connector_status_check",
            replace_existing=True,  # Replace job if it already exists from a previous run
            coalesce=True,  # Run job only once if multiple runs were missed
            max_instances=1,  # Allow only one concurrent instance of this job
            kwargs={
                "restart_connectors": settings.restart_connectors,
            },
        )
        scheduler.start()
        logger.info(f"APScheduler started. Job scheduled every {settings.job_frequency_seconds}s.")
    else:
        logger.warning("APScheduler job is disabled by settings.")

    yield

    if scheduler.running:
        logger.info("Shutting down... Stopping scheduler.")
        scheduler.shutdown()

    logger.info("Potassium API shut down.")


app = FastAPI(lifespan=lifespan, title=settings.app_name, version="0.1.0")
app.include_router(api_router, prefix="/api", tags=["API"])


@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": f"Welcome to {settings.app_name}!"}
