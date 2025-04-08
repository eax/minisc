import pytest
from pydantic import ValidationError

from common.models import ClusterConfig, WorkerNodesConfig

def test_cluster_config_minimal():
    """Test minimal valid cluster config"""
    config = ClusterConfig(
        provider="aws",
        region="us-east-1",
        cluster_name="test-cluster",
        node_size="t2.medium"
    )
    
    assert config.provider == "aws"
    assert config.region == "us-east-1"
    assert config.cluster_name == "test-cluster"
    assert config.node_size == "t2.medium"
    assert config.admin_username is None
    assert config.tags is None

def test_cluster_config_full_azure():
    """Test full Azure cluster config"""
    config = ClusterConfig(
        provider="azure",
        region="eastus",
        cluster_name="azure-cluster",
        node_size="Standard_D2s_v3",
        admin_username="azureuser",
        admin_password="Password123!",
        resource_group_name="test-rg",
        vnet_name="test-vnet",
        subnet_name="test-subnet",
        tags={"environment": "test", "project": "k8s"}
    )
    
    assert config.provider == "azure"
    assert config.resource_group_name == "test-rg"
    assert config.vnet_name == "test-vnet"
    assert config.tags == {"environment": "test", "project": "k8s"}

def test_cluster_config_full_aws():
    """Test full AWS cluster config"""
    config = ClusterConfig(
        provider="aws",
        region="us-east-1",
        cluster_name="aws-cluster",
        node_size="t2.medium",
        ssh_key_name="my-key",
        tags={"environment": "test", "project": "k8s"}
    )
    
    assert config.provider == "aws"
    assert config.ssh_key_name == "my-key"
    assert config.tags == {"environment": "test", "project": "k8s"}

def test_worker_nodes_config():
    """Test worker nodes config"""
    config = WorkerNodesConfig(
        provider="azure",
        region="eastus",
        cluster_name="worker-cluster",
        node_size="Standard_D2s_v3",
        worker_count=3,
        join_token="sample-token-123"
    )
    
    assert config.provider == "azure"
    assert config.worker_count == 3
    assert config.join_token == "sample-token-123"

def test_worker_nodes_config_missing_worker_count():
    """Test that worker_count is required"""
    with pytest.raises(ValidationError) as excinfo:
        WorkerNodesConfig(
            provider="azure",
            region="eastus",
            cluster_name="worker-cluster",
            node_size="Standard_D2s_v3"
        )
    
    assert "worker_count" in str(excinfo.value)