from kubernetes_deployer import KubernetesDeployer
from master_node_deployer import MasterNodeDeployer
from worker_nodes_deployer import WorkerNodesDeployer


def main():
    region = 'us-east-1'
    key_name = 'your-key-pair'
    instance_type = 't2.medium'
    num_workers = 2

    # Initialize deployers
    deployer = KubernetesDeployer(region)
    master_deployer = MasterNodeDeployer(region)
    worker_deployer = WorkerNodesDeployer(region)

    # Create VPC, Subnet, and Security Group
    vpc_id, subnet_id = deployer.create_vpc_and_subnet()
    security_group_id = deployer.create_security_group(vpc_id)

    # Deploy Master Node
    master_deployer.deploy_master_node(security_group_id, subnet_id, key_name, instance_type)

    # Deploy Worker Nodes
    worker_deployer.deploy_worker_nodes(security_group_id, subnet_id, key_name, num_workers, instance_type)


if __name__ == "__main__":
    main()