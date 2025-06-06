from pydantic.fields import Field
from pydantic_settings import BaseSettings
from pydantic_settings import PydanticBaseSettingsSource

from potassium.config.secrets.secret import SecretsSource


class SecretSettings(BaseSettings):
    secret_name: str = Field(
        ..., description="Name of the secret with '<protocol>://<name>' format"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            SecretsSource(settings_cls),
            file_secret_settings,
        )
