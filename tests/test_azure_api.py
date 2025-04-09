import pytest
from fastapi.testclient import TestClient
from minisc.api.main import app

client = TestClient(app)

@pytest.fixture
def head_node_request():
    return {
        "resource_group_name": "k8s-resource-group",
        "head_node_name": "k8s-master",
        "location": "eastus",
        "head_node_size": "Standard_D2s_v3",
        "vnet_name": "k8s-vnet",
        "subnet_name": "k8s-subnet",
        "admin_username": "azureuser",
        "admin_password": "KubeAdm1n2024!"
    }

@pytest.fixture
def worker_nodes_request():
    return {
        "resource_group_name": "k8s-resource-group",
        "vmss_name": "k8s-workers",
        "location": "eastus",
        "worker_node_size": "Standard_D2s_v3",
        "worker_node_count": 2,
        "vnet_name": "k8s-vnet",
        "subnet_name": "k8s-subnet",
        "join_token": "sample-join-token",
        "admin_username": "azureuser",
        "admin_password": "KubeAdm1n2024!"
    }

def test_deploy_head_node(head_node_request):
    response = client.post("/deploy/head-node", json=head_node_request)
    assert response.status_code == 200
    assert "message" in response.json()
    assert "head_node_ip" in response.json()

def test_deploy_worker_nodes(worker_nodes_request):
    response = client.post("/deploy/worker-nodes", json=worker_nodes_request)
    assert response.status_code == 200
    assert "message" in response.json()