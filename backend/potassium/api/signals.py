import asyncio
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from kafka.errors import KafkaError
from loguru import logger
from pydantic import BaseModel, Field

from potassium.debezium.client import KafkaConnectClient
from potassium.debezium.exceptions import KafkaConnectAPIError
from potassium.debezium.models import ConnectorConfig
from potassium.dependencies import get_kafka_client, get_kafka_connect_client
from potassium.kafka.client import KafkaClient

router = APIRouter()


class DataCondition(BaseModel):
    data_collection: str
    filter: str


class SignalRequest(BaseModel):
    connector_name: str = Field(..., description="The name of the connector to signal.")
    type: Literal["execute-snapshot"] = Field(
        default="execute-snapshot", description="The type of signal to send to Debezium."
    )
    signal_type: Literal["blocking", "incremental"] = "blocking"
    data_collections: list[str] = Field(
        ..., description="List of fully-qualified table names to include in the snapshot"
    )
    additional_conditions: list[DataCondition] | None = Field(
        default=None,
        description="A list filters ",
    )

    @property
    def debezium_signal_payload(self) -> dict:
        signal_id = f"potassium-{uuid.uuid4()}"
        logger.info(f"Generating Debezium payload for signal ID: {signal_id}")

        final_payload = {
            "id": signal_id,
            "type": self.type,
            "data": {
                "type": self.signal_type,
                "data-collections": self.data_collections,
                "additional-conditions": self.additional_conditions,
            },
        }

        logger.info(f"Generated payload: {final_payload}")
        return final_payload


class SignalResponse(BaseModel):
    signal_id: str
    status: str
    details: str


@router.post("/send_signal", response_model=SignalResponse)
async def send_signal(
    signal_request: SignalRequest,
    kafka_client: KafkaClient = Depends(get_kafka_client),
    kafka_connect_client: KafkaConnectClient = Depends(get_kafka_connect_client),
) -> SignalResponse:
    signal_id = f"potassium-{uuid.uuid4()}"
    try:
        logger.info(f"Fetching configuration for connector '{signal_request.connector_name}' from Kafka Connect.")
        # This client would return a Pydantic model of the config
        connector_config: ConnectorConfig = await kafka_connect_client.get_connector_config(
            signal_request.connector_name
        )

        signalling_topic = connector_config.signal_data_collection

        if not signalling_topic:
            logger.error(
                f"Connector '{signal_request.connector_name}' does not have 'signal.data.collection' configured"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Connector '{signal_request.connector_name}' does not have a signalling topic configured.",
            )
    except KafkaConnectAPIError as e:
        logger.error(f"Error fetching config from Kafka Connect for '{signal_request.connector_name}': {e}")
        if e.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connector '{signal_request.connector_name}' not found on Kafka Connect.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Could not communicate with Kafka Connect: {e}"
            )

    logger.info(f"Sending signal to topic '{signalling_topic}' for connector '{signal_request.connector_name}'")

    try:
        await kafka_client.send_event(
            topic=signalling_topic, key=signal_id, value=signal_request.debezium_signal_payload
        )

        return SignalResponse(
            signal_id=signal_id, status="SENT", details=f"Signal successfully sent to topic '{signalling_topic}'."
        )
    except KafkaError as e:
        logger.error(f"Failed to send signal to Kafka: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Failed to deliver signal to Kafka: {e}"
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request to Kafka timed out. The signal may not have been sent.",
        )
