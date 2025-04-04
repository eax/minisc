from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src import HeadNodeDeployer, WorkerNodesDeployer, load_config

app = FastAPI()

# Load configuration
config = load_config()

# Request models
class HeadNodeRequest(BaseModel):
    resource_group_name: str
    head_node_name: str
    location: str
    head_node_size: str
    vnet_name: str
    subnet_name: str
    admin_username: str
    admin_password: str

class WorkerNodesRequest(BaseModel):
    resource_group_name: str
    vmss_name: str
    location: str
    worker_node_size: str
    worker_node_count: int
    vnet_name: str
    subnet_name: str
    join_token: str
    admin_username: str
    admin_password: str

@app.post("/deploy/head-node")
def deploy_head_node(request: HeadNodeRequest):
    try:
        head_deployer = HeadNodeDeployer(
            config['tenant_id'],
            config['client_id'],
            config['client_secret'],
            config['subscription_id']
        )
        head_deployer.create_resource_group(request.resource_group_name, request.location)
        head_node, head_node_ip = head_deployer.create_kubernetes_head_node(
            request.resource_group_name,
            request.head_node_name,
            request.location,
            request.head_node_size,
            request.vnet_name,
            request.subnet_name,
            request.admin_username,
            request.admin_password
        )
        return {
            "message": "Kubernetes head node deployment complete!",
            "head_node_ip": head_node_ip
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deploy/worker-nodes")
def deploy_worker_nodes(request: WorkerNodesRequest):
    try:
        worker_deployer = WorkerNodesDeployer(
            config['tenant_id'],
            config['client_id'],
            config['client_secret'],
            config['subscription_id']
        )
        worker_deployer.create_worker_nodes(
            request.resource_group_name,
            request.vmss_name,
            request.location,
            request.worker_node_size,
            request.worker_node_count,
            request.vnet_name,
            request.subnet_name,
            request.join_token,
            request.admin_username,
            request.admin_password
        )
        return {"message": "Worker nodes deployment complete!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))