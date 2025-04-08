import pytest
from unittest.mock import patch, MagicMock

from common.provider_factory import CloudProviderFactory, CloudProvider

@pytest.fixture
def azure_config():
    return {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id", 
        "client_secret": "test-client-secret",
        "subscription_id": "test-subscription-id"
    }

@pytest.fixture
def aws_config():
    return {
        "region": "us-west-2"
    }

@patch("common.provider_factory.AzureHeadNodeDeployer")
@patch("common.provider_factory.AzureWorkerNodesDeployer")
def test_get_azure_provider(mock_azure_worker, mock_azure_head, azure_config):
    # Test getting Azure provider
    result = CloudProviderFactory.get_provider("azure", azure_config)
    
    # Verify correct provider type
    assert "head_node_deployer" in result
    assert "worker_nodes_deployer" in result
    
    # Verify objects were created with correct config
    mock_azure_head.assert_called_once_with(
        azure_config["tenant_id"],
        azure_config["client_id"],
        azure_config["client_secret"],
        azure_config["subscription_id"]
    )
    
    mock_azure_worker.assert_called_once_with(
        azure_config["tenant_id"],
        azure_config["client_id"],
        azure_config["client_secret"],
        azure_config["subscription_id"]
    )

@patch("common.provider_factory.AwsKubernetesDeployer")
@patch("common.provider_factory.AwsMasterNodeDeployer")
@patch("common.provider_factory.AwsWorkerNodesDeployer")
def test_get_aws_provider(mock_aws_worker, mock_aws_master, mock_aws_k8s, aws_config):
    # Test getting AWS provider
    result = CloudProviderFactory.get_provider("aws", aws_config)
    
    # Verify correct provider type
    assert "kubernetes_deployer" in result
    assert "head_node_deployer" in result
    assert "worker_nodes_deployer" in result
    
    # Verify objects were created with correct region
    mock_aws_k8s.assert_called_once_with(aws_config["region"])
    mock_aws_master.assert_called_once_with(aws_config["region"])
    mock_aws_worker.assert_called_once_with(aws_config["region"])

def test_get_invalid_provider():
    # Test with invalid provider
    with pytest.raises(ValueError) as excinfo:
        CloudProviderFactory.get_provider("invalid-provider", {})
    
    assert "Unsupported cloud provider" in str(excinfo.value)