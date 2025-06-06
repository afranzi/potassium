from moto import mock_aws
from pytest_kubernetes.providers import AClusterManager

from potassium.config.secrets.settings import SecretSettings
from tests.helpers import set_up_secret


class TestSecretSettings(SecretSettings):
    username: str
    password: str


def test_get_k8s_secret(k8s_potassium_cluster: AClusterManager) -> None:
    secret = TestSecretSettings(secret_name="k8s://potassium/potassium-db-creds")

    assert secret.username == "k8s_test_user"
    assert secret.password == "ILovePotatoes"


@mock_aws
def test_get_aws_secret() -> None:
    secret_name = "potassium-db-creds"
    set_up_secret(
        secret_name=secret_name,
        content={"username": "potato", "password": "ILovePotatoes"},
    )

    secret = TestSecretSettings(secret_name=f"aws://{secret_name}")

    assert secret.username == "potato"
    assert secret.password == "ILovePotatoes"
