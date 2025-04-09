from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os
from functools import lru_cache
from dotenv import load_dotenv

from minisc.common.provider_factory import CloudProviderFactory
from minisc.common.models import ClusterConfig, WorkerNodesConfig

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Configuration loading
@lru_cache()
def get_settings():
    return {
        # Common settings
        "default_provider": os.environ.get("CLOUD_PROVIDER", "azure"),
        
        # Azure settings
        "tenant_id": os.environ.get("AZURE_TENANT_ID", ""),
        "client_id": os.environ.get("AZURE_CLIENT_ID", ""),
        "client_secret": os.environ.get("AZURE_CLIENT_SECRET", ""),
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID", ""),
        
        # AWS settings
        "region": os.environ.get("AWS_REGION", "us-east-1"),
        "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
    }

# Provider adapters to normalize differences
def deploy_head_node_azure(provider, config):
    head_deployer = provider["head_node_deployer"]
    head_deployer.create_resource_group(config.resource_group_name, config.region)
    return head_deployer.create_kubernetes_head_node(
        config.resource_group_name,
        config.cluster_name,
        config.region,
        config.node_size,
        config.vnet_name,
        config.subnet_name,
        config.admin_username,
        config.admin_password
    )

def deploy_head_node_aws(provider, config):
    kubernetes_deployer = provider["kubernetes_deployer"]
    head_deployer = provider["head_node_deployer"]
    
    vpc_id, subnet_id = kubernetes_deployer.create_vpc_and_subnet()
    security_group_id = kubernetes_deployer.create_security_group(vpc_id)
    
    return head_deployer.deploy_master_node(
        security_group_id=security_group_id,
        subnet_id=subnet_id,
        key_name=config.ssh_key_name,
        instance_type=config.node_size
    )

# API endpoints
@app.post("/deploy/head-node")
def deploy_head_node(config: ClusterConfig):
    settings = get_settings()
    provider_type = config.provider or settings["default_provider"]
    
    try:
        provider = CloudProviderFactory.get_provider(provider_type, settings)
        
        if provider_type == "azure":
            head_node, head_node_ip = deploy_head_node_azure(provider, config)
            return {
                "message": "Kubernetes head node deployment complete!",
                "provider": "azure",
                "head_node_ip": head_node_ip
            }
        else:  # AWS
            instance = deploy_head_node_aws(provider, config)
            return {
                "message": "Kubernetes master node deployment complete!",
                "provider": "aws",
                "instance_id": instance.id if instance else None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deploy/worker-nodes")
def deploy_worker_nodes(config: WorkerNodesConfig):
    settings = get_settings()
    provider_type = config.provider or settings["default_provider"]
    
    try:
        provider = CloudProviderFactory.get_provider(provider_type, settings)
        
        if provider_type == "azure":
            worker_deployer = provider["worker_nodes_deployer"]
            worker_deployer.create_worker_nodes(
                config.resource_group_name,
                f"{config.cluster_name}-workers",
                config.region,
                config.node_size,
                config.worker_count,
                config.vnet_name,
                config.subnet_name,
                config.join_token,
                config.admin_username,
                config.admin_password
            )
            return {"message": "Worker nodes deployment complete!", "provider": "azure"}
        else:  # AWS
            kubernetes_deployer = provider["kubernetes_deployer"]
            worker_deployer = provider["worker_nodes_deployer"]
            
            vpc_id, subnet_id = kubernetes_deployer.create_vpc_and_subnet()
            security_group_id = kubernetes_deployer.create_security_group(vpc_id)
            
            worker_deployer.deploy_worker_nodes(
                security_group_id=security_group_id,
                subnet_id=subnet_id,
                key_name=config.ssh_key_name,
                num_workers=config.worker_count,
                instance_type=config.node_size
            )
            return {"message": f"{config.worker_count} worker nodes deployment complete!", "provider": "aws"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cluster-info")
def get_cluster_info(config: ClusterConfig):
    settings = get_settings()
    provider_type = config.provider or settings["default_provider"]
    
    try:
        provider = CloudProviderFactory.get_provider(provider_type, settings)
        
        if provider_type == "azure":
            # Implement Azure cluster info retrieval
            return {"message": "Azure cluster info retrieval not implemented yet"}
        else:  # AWS
            master_deployer = provider["head_node_deployer"]
            cluster_info = master_deployer.get_cluster_info(config.ssh_key_name)
            if cluster_info:
                return {"message": "Cluster information retrieved successfully!", "provider": "aws"}
            else:
                raise HTTPException(status_code=500, detail="Failed to retrieve cluster information.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))