from typing import Optional, Dict, Any
from pydantic import BaseModel

class ClusterConfig(BaseModel):
    """Common configuration for both cloud providers"""
    provider: str  # "aws" or "azure"
    region: str
    cluster_name: str
    node_size: str  # Will map to instance_type in AWS or vm_size in Azure
    admin_username: Optional[str] = None
    admin_password: Optional[str] = None
    ssh_key_name: Optional[str] = None
    
    # Azure specific (will be ignored for AWS)
    resource_group_name: Optional[str] = None
    vnet_name: Optional[str] = None
    subnet_name: Optional[str] = None
    
    # Extended configurations as needed
    tags: Optional[Dict[str, str]] = None
    custom_config: Optional[Dict[str, Any]] = None

class WorkerNodesConfig(ClusterConfig):
    worker_count: int
    join_token: Optional[str] = None  # Required for Azure