import re
from typing import Any, Tuple, Callable

from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings
from pydantic_settings import PydanticBaseSettingsSource

from potassium.config.secrets import aws, k8s


class SecretsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        PydanticBaseSettingsSource.__init__(self, settings_cls)
        self._cache: dict[str, Any] | None = None

    @staticmethod
    def parse_secret_name(secret_name) -> Tuple[str | None, str | None]:
        secret_regex = re.compile(r"(?P<protocol>[\w-]+)://(?P<identifier>.+)")
        search_result = secret_regex.search(secret_name)
        if search_result:
            groups = search_result.groupdict()
            return groups.get("protocol"), groups.get("identifier")
        return None, None

    def get_secret(self, secret_name: str | None) -> dict:
        if not secret_name or not isinstance(secret_name, str):
            return {}

        protocol, secret_id = self.parse_secret_name(secret_name=secret_name)

        if not protocol or not secret_id:
            raise RuntimeError(f"Could not parse secret URI: '{secret_name}'")

        protocols: dict[str, Callable[[str], dict]] = {
            "aws": aws.get_secret,
            "k8s": k8s.get_secret,
        }

        load_function = protocols.get(protocol.lower())
        if load_function:
            return load_function(secret_id)
        else:
            raise RuntimeError(f"Protocol {protocol} not supported")

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        if field_name == "secret_name":
            return None, field_name, False

        if self._cache is None:
            secret_name = self.current_state.get("secret_name")
            self._cache = self.get_secret(secret_name)

        val = self._cache.get(field_name)
        return val, field_name, False

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value

        return d
