import base64

from kubernetes import client, config
from pydantic_settings import BaseSettings, SettingsConfigDict


class KubeConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="potassium_")
    kube_config_path: str | None = None

    @classmethod
    def load_config(cls) -> None:
        settings = KubeConfigSettings()

        if settings.kube_config_path:
            config.load_config(kube_config_path=settings.kube_config_path)
        else:
            config.load_incluster_config()


def get_pod_namespace() -> str:
    try:
        return (
            open("/var/run/secrets/kubernetes.io/serviceaccount/namespace")
            .read()
            .strip()
        )
    except FileNotFoundError:
        return "default"


def get_secret(secret_id: str) -> dict:
    parts = secret_id.split("/")

    namespace: str
    secret_name: str

    if len(parts) == 2:
        namespace, secret_name = parts
    elif len(parts) == 1:
        secret_name = parts[0]
        namespace = get_pod_namespace()
    else:
        raise RuntimeError(f"Invalid K8s secret identifier format: '{secret_id}'")

    KubeConfigSettings.load_config()
    v1 = client.CoreV1Api()

    data: dict[str, str] = v1.read_namespaced_secret(
        name=secret_name, namespace=namespace
    ).data
    return {key: base64.b64decode(value) for key, value in data.items()}
