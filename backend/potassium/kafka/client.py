import json
from typing import Literal

from kafka import KafkaProducer
from pydantic import Field, SecretStr

from potassium.config.secrets.settings import SecretSettings

SecurityProtocolType = Literal["PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL"]
SASLMechanismType = Literal["PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512", "GSSAPI", "OAUTHBEARER"]


class KafkaSettings(SecretSettings):
    client_id: str = Field(default="potassium", description="Logical name for the application instance")
    bootstrap_servers: str = Field(description="Comma-separated list of Kafka broker host:port pairs")
    security_protocol: SecurityProtocolType = Field(
        default="SASL_SSL", description="Security protocol used to communicate with brokers"
    )
    sasl_mechanism: SASLMechanismType = Field(
        default="SCRAM-SHA-512",
        description="The SASL mechanism to use for authentication. Depends on the broker's configuration.",
    )
    sasl_plain_username: str | None = Field(
        default=None, description="Username for SASL PLAIN or SCRAM authentication. Often sourced from a secret."
    )
    sasl_plain_password: SecretStr | None = Field(
        default=None,
        description="Password for SASL PLAIN or SCRAM authentication. Should always be sourced from a secret.",
    )


class KafkaClient:
    def __init__(self, settings: KafkaSettings) -> None:
        self.settings = settings
        self.producer = self.get_producer()

    def get_producer(self) -> KafkaProducer:
        return KafkaProducer(
            bootstrap_servers=self.settings.bootstrap_servers,
            client_id=self.settings.client_id,
            security_protocol=self.settings.security_protocol,
            sasl_plain_username=self.settings.sasl_plain_username,
            sasl_plain_password=self.settings.sasl_plain_password.get_secret_value()
            if self.settings.sasl_plain_password
            else None,
            sasl_mechanism=self.settings.sasl_mechanism,
            key_serializer=lambda k: k.encode("utf-8"),
            value_serializer=lambda v: json.dumps(v, separators=(",", ":"), indent=None).encode("utf-8"),
        )

    async def send_event(self, topic: str, key: str, value: dict) -> None:
        future = self.producer.send(topic=topic, key=key, value=value, partition=0)
        record_metadata = future.get(timeout=10)
        return record_metadata
