from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.kubernetes_deployer import KubernetesDeployer
from src.master_node_deployer import MasterNodeDeployer
from src.worker_nodes_deployer import WorkerNodesDeployer

app = FastAPI()

# Request models
class MasterNodeRequest(BaseModel):
    key_name: str
    instance_type: str
    region: str

class WorkerNodesRequest(BaseModel):
    key_name: str
    instance_type: str
    region: str
    num_workers: int

class ClusterInfoRequest(BaseModel):
    key_name: str
    region: str

@app.post("/deploy/master-node")
def deploy_master_node(request: MasterNodeRequest):
    try:
        # Initialize deployers
        deployer = KubernetesDeployer(request.region)
        master_deployer = MasterNodeDeployer(request.region)

        # Create VPC, Subnet, and Security Group
        vpc_id, subnet_id = deployer.create_vpc_and_subnet()
        security_group_id = deployer.create_security_group(vpc_id)

        # Deploy Master Node
        master_deployer.deploy_master_node(
            security_group_id=security_group_id,
            subnet_id=subnet_id,
            key_name=request.key_name,
            instance_type=request.instance_type
        )

        return {"message": "Master node deployment complete!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deploy/worker-nodes")
def deploy_worker_nodes(request: WorkerNodesRequest):
    try:
        # Initialize deployers
        deployer = KubernetesDeployer(request.region)
        worker_deployer = WorkerNodesDeployer(request.region)

        # Create VPC, Subnet, and Security Group
        vpc_id, subnet_id = deployer.create_vpc_and_subnet()
        security_group_id = deployer.create_security_group(vpc_id)

        # Deploy Worker Nodes
        worker_deployer.deploy_worker_nodes(
            security_group_id=security_group_id,
            subnet_id=subnet_id,
            key_name=request.key_name,
            num_workers=request.num_workers,
            instance_type=request.instance_type
        )

        return {"message": f"{request.num_workers} worker nodes deployment complete!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cluster-info")
def get_cluster_info(request: ClusterInfoRequest):
    try:
        # Initialize MasterNodeDeployer
        master_deployer = MasterNodeDeployer(request.region)

        # Retrieve cluster information
        cluster_info = master_deployer.get_cluster_info(request.key_name)

        if cluster_info:
            return {"message": "Cluster information retrieved successfully!"}
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve cluster information.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))