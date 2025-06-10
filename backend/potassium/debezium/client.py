from typing import List, Type

import httpx
from pydantic import TypeAdapter, ValidationError

from potassium.config.settings import kafka_connect_settings
from potassium.debezium.exceptions import KafkaConnectAPIError, ResponseParsingError
from potassium.debezium.models import ConnectorConfig, FullConnectorStatus, ModelType


class KafkaConnectClient:
    def __init__(self) -> None:
        self.config = kafka_connect_settings
        self._client = httpx.AsyncClient(base_url=self.config.uri, timeout=10)

    async def get_request(self, endpoint: str, response_model: Type[ModelType]) -> ModelType:
        try:
            response = await self._client.get(endpoint)
            response.raise_for_status()

            json_data = response.json()
            parsed_obj = response_model.model_validate(json_data)
            return parsed_obj
        except httpx.HTTPStatusError as e:
            raise KafkaConnectAPIError(
                message=f"HTTP error '{e.response.status_code}' for '{e.request.url}'",
                status_code=e.response.status_code,
                response_text=e.response.text,
            ) from e
        except httpx.RequestError as e:
            raise KafkaConnectAPIError(message=f"Request error for '{e.request.url}': {e}") from e
        except ValidationError as e:
            raise ResponseParsingError(
                message=f"Failed to parse response for '{endpoint}' into {response_model.__name__}: {response.json()}"
            ) from e

    async def list_connectors(self) -> list[str]:
        try:
            response = await self._client.get("/connectors")
            response.raise_for_status()
            str_list_adapter = TypeAdapter(List[str])
            return str_list_adapter.validate_python(response.json())
        except (httpx.RequestError, ValidationError) as e:
            raise KafkaConnectAPIError(f"Failed to list connectors: {e}") from e

    async def get_connector_config(self, connector_name: str) -> ConnectorConfig:
        return await self.get_request(endpoint=f"/connectors/{connector_name}/config", response_model=ConnectorConfig)

    async def get_connector_status(self, connector_name: str) -> FullConnectorStatus:
        return await self.get_request(
            endpoint=f"/connectors/{connector_name}/status", response_model=FullConnectorStatus
        )

    async def restart_connectors(self, connector_name: str) -> None:
        try:
            response = await self._client.post(f"/connectors/{connector_name}/restart?includeTasks=true")
            response.raise_for_status()
        except httpx.RequestError as e:
            raise KafkaConnectAPIError(f"Failed to restart connector: {e}") from e
