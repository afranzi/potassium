from typing import List, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

ModelType = TypeVar("ModelType", bound=BaseModel)
ConnectorStateType = Literal["RUNNING", "FAILED", "RESTARTING", "PAUSED", "UNASSIGNED"]
ConnectorType = Literal["source", "sink"]
SnapshotType = Literal[
    "initial_only",
    "initial",
    "recovery",
    "schema_only_recovery",
    "schema_only",
    "always",
    "when_needed",
    "never",
    "no_data",
]
SignalChannelType = Literal["kafka", "source", "jmx", "file"]


class ConnectorTask(BaseModel):
    id: int
    state: ConnectorStateType
    worker_id: str
    trace: str | None = None


class ConnectorStatus(BaseModel):
    state: ConnectorStateType
    worker_id: str


class FullConnectorStatus(BaseModel):
    name: str
    connector: ConnectorStatus
    tasks: List[ConnectorTask]
    type: ConnectorType


class ConnectorConfig(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    name: str
    connector_class: str = Field(..., alias="connector.class")
    table_include_list: Optional[str] = Field(None, alias="table.include.list")

    signal_data_collection: Optional[str] = Field(None, alias="signal.data.collection")
    signal_channels: Optional[SignalChannelType] = Field(None, alias="signal.enabled.channels")
    signal_topic: Optional[str] = Field(None, alias="signal.kafka.topic")
    snapshot_mode: Optional[SnapshotType] = Field(None, alias="snapshot.mode")
