import pytest
from fastapi.testclient import TestClient
from minisc.api.main import app

client = TestClient(app)

@pytest.fixture
def master_node_request():
    return {
        "key_name": "your-key-pair",
        "instance_type": "t2.medium",
        "region": "us-east-1"
    }

@pytest.fixture
def worker_nodes_request():
    return {
        "key_name": "your-key-pair",
        "instance_type": "t2.medium",
        "region": "us-east-1",
        "num_workers": 2
    }

@pytest.fixture
def cluster_info_request():
    return {
        "key_name": "your-key-pair",
        "region": "us-east-1"
    }

def test_deploy_master_node(master_node_request):
    response = client.post("/deploy/master-node", json=master_node_request)
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Master node deployment complete!"

def test_deploy_worker_nodes(worker_nodes_request):
    response = client.post("/deploy/worker-nodes", json=worker_nodes_request)
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "2 worker nodes deployment complete!"

def test_get_cluster_info(cluster_info_request):
    response = client.post("/cluster-info", json=cluster_info_request)
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Cluster information retrieved successfully!"