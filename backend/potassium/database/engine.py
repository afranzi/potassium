from abc import ABC, abstractmethod

from pydantic_settings import BaseSettings
from sqlalchemy import Engine, inspect
from sqlalchemy.engine.interfaces import ReflectedColumn


class SchemaInspector:
    def __init__(self, engine: Engine) -> None:
        self.inspector = inspect(engine)

    def get_columns(self, schema: str, table: str) -> list[ReflectedColumn]:
        return self.inspector.get_columns(schema=schema, table_name=table)


class EngineCredentials(BaseSettings, ABC):
    driver_name: str

    @property
    @abstractmethod
    def engine(self) -> Engine: ...

    @property
    def inspector(self) -> SchemaInspector:
        return SchemaInspector(self.engine)
