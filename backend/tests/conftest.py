import os

import pytest
from pytest_kubernetes.providers import select_provider_manager

from tests import fixture_file_path


@pytest.fixture(scope="session")
def k8s_potassium_cluster(request):
    # Use k3d for a lightweight, fast-starting cluster. (brew install k3d)
    cluster_manager = select_provider_manager("k3d")("potassium-test-cluster")

    cluster_manager.reset()

    cluster_manager.apply(fixture_file_path("potassium-setup.yaml"))

    # Wait for the resources to be created to avoid race conditions in tests
    cluster_manager.wait("namespace/potassium", "jsonpath='{.metadata.name}'=potassium")
    cluster_manager.wait(
        "secret/potassium-db-creds",
        "jsonpath='{.metadata.name}'=potassium-db-creds",
        namespace="potassium",
    )

    os.environ["POTASSIUM_KUBE_CONFIG_PATH"] = str(cluster_manager.kubeconfig)

    yield cluster_manager
    cluster_manager.delete()
