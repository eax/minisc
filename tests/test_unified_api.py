import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from minisc.api.main import app, get_settings
from minisc.common.provider_factory import CloudProviderFactory

client = TestClient(app)

@pytest.fixture
def mock_settings():
    return {
        "default_provider": "azure",
        "tenant_id": "mock-tenant-id",
        "client_id": "mock-client-id",
        "client_secret": "mock-client-secret",
        "subscription_id": "mock-subscription-id",
        "region": "us-east-1",
        "aws_access_key_id": "mock-aws-key",
        "aws_secret_access_key": "mock-aws-secret"
    }

@pytest.fixture
def azure_head_node_request():
    return {
        "provider": "azure",
        "cluster_name": "k8s-master",
        "resource_group_name": "k8s-resource-group",
        "region": "eastus",
        "node_size": "Standard_D2s_v3",
        "vnet_name": "k8s-vnet",
        "subnet_name": "k8s-subnet",
        "admin_username": "azureuser",
        "admin_password": "KubeAdm1n2024!"
    }

@pytest.fixture
def aws_head_node_request():
    return {
        "provider": "aws",
        "cluster_name": "k8s-cluster",
        "region": "us-east-1",
        "node_size": "t2.medium",
        "ssh_key_name": "test-key-pair"
    }

@pytest.fixture
def azure_worker_nodes_request():
    return {
        "provider": "azure",
        "cluster_name": "k8s-workers",
        "resource_group_name": "k8s-resource-group",
        "region": "eastus",
        "node_size": "Standard_D2s_v3",
        "worker_count": 2,
        "vnet_name": "k8s-vnet",
        "subnet_name": "k8s-subnet",
        "join_token": "sample-join-token",
        "admin_username": "azureuser",
        "admin_password": "KubeAdm1n2024!"
    }

@pytest.fixture
def aws_worker_nodes_request():
    return {
        "provider": "aws",
        "cluster_name": "k8s-cluster",
        "region": "us-east-1",
        "node_size": "t2.medium",
        "worker_count": 2,
        "ssh_key_name": "test-key-pair"
    }

@patch("api.main.get_settings")
@patch("api.main.CloudProviderFactory.get_provider")
def test_deploy_azure_head_node(mock_get_provider, mock_get_settings, mock_settings, azure_head_node_request):
    mock_get_settings.return_value = mock_settings

    # Create mocks for Azure providers
    mock_head_node_deployer = MagicMock()
    mock_head_node_deployer.create_resource_group.return_value = None
    mock_head_node_deployer.create_kubernetes_head_node.return_value = (MagicMock(), "10.0.0.1")

    # Mock the provider factory
    mock_get_provider.return_value = {
        "head_node_deployer": mock_head_node_deployer,
        "worker_nodes_deployer": MagicMock()
    }

    response = client.post("/deploy/head-node", json=azure_head_node_request)
    
    assert response.status_code == 200
    assert "message" in response.json()
    assert "head_node_ip" in response.json()
    assert response.json()["head_node_ip"] == "10.0.0.1"

    # Verify the head node deployer was called with correct parameters
    mock_head_node_deployer.create_resource_group.assert_called_once_with(
        azure_head_node_request["resource_group_name"], 
        azure_head_node_request["region"]
    )
    mock_head_node_deployer.create_kubernetes_head_node.assert_called_once()

@patch("api.main.get_settings")
@patch("api.main.CloudProviderFactory.get_provider")
def test_deploy_aws_head_node(mock_get_provider, mock_get_settings, mock_settings, aws_head_node_request):
    mock_get_settings.return_value = mock_settings
    
    # Create mocks for AWS providers
    mock_kubernetes_deployer = MagicMock()
    mock_kubernetes_deployer.create_vpc_and_subnet.return_value = ("vpc-12345", "subnet-12345")
    mock_kubernetes_deployer.create_security_group.return_value = "sg-12345"
    
    mock_head_deployer = MagicMock()
    mock_instance = MagicMock()
    mock_instance.id = "i-12345"
    mock_head_deployer.deploy_master_node.return_value = mock_instance
    
    # Mock the provider factory
    mock_get_provider.return_value = {
        "kubernetes_deployer": mock_kubernetes_deployer,
        "head_node_deployer": mock_head_deployer,
        "worker_nodes_deployer": MagicMock()
    }
    
    response = client.post("/deploy/head-node", json=aws_head_node_request)
    
    assert response.status_code == 200
    assert "message" in response.json()
    assert "instance_id" in response.json()
    assert response.json()["instance_id"] == "i-12345"
    
    # Verify the AWS deployers were called with correct parameters
    mock_kubernetes_deployer.create_vpc_and_subnet.assert_called_once()
    mock_kubernetes_deployer.create_security_group.assert_called_once_with("vpc-12345")
    mock_head_deployer.deploy_master_node.assert_called_once_with(
        security_group_id="sg-12345",
        subnet_id="subnet-12345",
        key_name=aws_head_node_request["ssh_key_name"],
        instance_type=aws_head_node_request["node_size"]
    )

@patch("api.main.get_settings")
@patch("api.main.CloudProviderFactory.get_provider")
def test_deploy_azure_worker_nodes(mock_get_provider, mock_get_settings, mock_settings, azure_worker_nodes_request):
    mock_get_settings.return_value = mock_settings
    
    # Create mocks for Azure providers
    mock_worker_deployer = MagicMock()
    
    # Mock the provider factory
    mock_get_provider.return_value = {
        "head_node_deployer": MagicMock(),
        "worker_nodes_deployer": mock_worker_deployer
    }
    
    response = client.post("/deploy/worker-nodes", json=azure_worker_nodes_request)
    
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["provider"] == "azure"
    
    # Verify worker nodes deployer was called with correct parameters
    mock_worker_deployer.create_worker_nodes.assert_called_once()

@patch("api.main.get_settings")
@patch("api.main.CloudProviderFactory.get_provider")
def test_deploy_aws_worker_nodes(mock_get_provider, mock_get_settings, mock_settings, aws_worker_nodes_request):
    mock_get_settings.return_value = mock_settings
    
    # Create mocks for AWS providers
    mock_kubernetes_deployer = MagicMock()
    mock_kubernetes_deployer.create_vpc_and_subnet.return_value = ("vpc-12345", "subnet-12345")
    mock_kubernetes_deployer.create_security_group.return_value = "sg-12345"
    
    mock_worker_deployer = MagicMock()
    
    # Mock the provider factory
    mock_get_provider.return_value = {
        "kubernetes_deployer": mock_kubernetes_deployer,
        "head_node_deployer": MagicMock(),
        "worker_nodes_deployer": mock_worker_deployer
    }
    
    response = client.post("/deploy/worker-nodes", json=aws_worker_nodes_request)
    
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["provider"] == "aws"
    
    # Verify AWS deployers were called correctly
    mock_kubernetes_deployer.create_vpc_and_subnet.assert_called_once()
    mock_kubernetes_deployer.create_security_group.assert_called_once_with("vpc-12345")
    mock_worker_deployer.deploy_worker_nodes.assert_called_once_with(
        security_group_id="sg-12345",
        subnet_id="subnet-12345",
        key_name=aws_worker_nodes_request["ssh_key_name"],
        num_workers=aws_worker_nodes_request["worker_count"],
        instance_type=aws_worker_nodes_request["node_size"]
    )