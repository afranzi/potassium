from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PotassiumSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="potassium_", extra="ignore")

    # --- General Application Settings ---
    app_name: str = "Potassium API"
    debug: bool = Field(default=False, description="Enable debug level logging")
    slack_secret: str | None = Field(default=None, description="Enable slack apprise notifications")
    kafka_secret: str = Field(..., description="Kafka secret with client credentials")

    # --- Background Job Settings ---
    job_enabled: bool = Field(default=True, description="Enable or disable the periodic connector status check job.")
    job_frequency_seconds: int = Field(default=60, gt=0, description="Frequency in seconds for the status check job.")
    restart_connectors: bool = Field(default=True, description="Restart failed connectors automatically")


class KafkaConnectSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="kafka_connect_")

    uri: str = "https://kafka-connect.data.lokalise.cloud"

    def endpoint(self, url: str) -> str:
        return f"{self.uri}/{url}"


settings = PotassiumSettings()
kafka_connect_settings = KafkaConnectSettings()
