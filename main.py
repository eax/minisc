import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def deploy_azure_cluster(deploy_workers=True):
    """Deploy a Kubernetes cluster on Azure"""
    from minisc.azure.kubernetes_deployer import load_config
    from minisc.azure.head_node import HeadNodeDeployer
    from minisc.azure.worker_nodes import WorkerNodesDeployer
    
    print("=== Deploying Azure Kubernetes Cluster ===")
    
    # Load configuration from environment variables
    config = load_config()
    
    # Create head node deployer
    head_deployer = HeadNodeDeployer(
        config['tenant_id'], 
        config['client_id'], 
        config['client_secret'], 
        config['subscription_id']
    )
    
    # Create resource group
    head_deployer.create_resource_group(config['resource_group_name'], config['location'])
    
    # Deploy Kubernetes head node
    head_node, head_node_ip = head_deployer.create_kubernetes_head_node(
        config['resource_group_name'],
        config['head_node_name'],
        config['location'],
        config['head_node_size'],
        config['vnet_name'],
        config['subnet_name'],
        config['admin_username'],
        config['admin_password']
    )
    
    print("\nKubernetes head node deployment complete!")
    print(f"Head node public IP: {head_node_ip}")
    
    # Handle worker node deployment
    if deploy_workers:
        print("To deploy worker nodes, you will need to:")
        print("1. SSH into the head node")
        print("2. Run: sudo kubeadm token create --print-join-command")
        print("3. Use the output as the join token\n")
        
        # Prompt user to deploy worker nodes
        deploy_workers_now = input("Do you want to deploy worker nodes now? (yes/no): ").strip().lower()
        if deploy_workers_now == "yes":
            # Get the join token from the user
            join_token = input("Enter the Kubernetes join token (from the head node): ").strip()
            
            # Create worker nodes deployer
            worker_deployer = WorkerNodesDeployer(
                config['tenant_id'], 
                config['client_id'], 
                config['client_secret'], 
                config['subscription_id']
            )
            
            # Deploy worker nodes
            worker_deployer.create_worker_nodes(
                config['resource_group_name'],
                config['vmss_name'],
                config['location'],
                config['worker_node_size'],
                config['worker_node_count'],
                config['vnet_name'],
                config['subnet_name'],
                join_token,
                config['admin_username'],
                config['admin_password']
            )
            
            print("\nAzure worker nodes deployment complete!")
        else:
            print("Worker nodes deployment skipped. You can deploy them later using --component workers")
    
    return {"provider": "azure", "head_node_ip": head_node_ip}

def deploy_aws_cluster(deploy_master=True, deploy_workers=True):
    """Deploy a Kubernetes cluster on AWS"""
    from minisc.aws.kubernetes_deployer import KubernetesDeployer
    from minisc.aws.master_node_deployer import MasterNodeDeployer
    from minisc.aws.worker_nodes_deployer import WorkerNodesDeployer
    
    print("=== Deploying AWS Kubernetes Cluster ===")
    
    # Load configuration from environment variables
    region = os.environ.get('AWS_REGION', 'us-east-1')
    key_name = os.environ.get('AWS_KEY_NAME', 'your-key-pair')
    instance_type = os.environ.get('AWS_INSTANCE_TYPE', 't2.medium')
    num_workers = int(os.environ.get('AWS_WORKER_COUNT', '2'))
    
    print(f"Region: {region}")
    print(f"Key Name: {key_name}")
    print(f"Instance Type: {instance_type}")
    print(f"Number of Workers: {num_workers}")
    
    # Initialize deployers
    deployer = KubernetesDeployer(region)
    
    # Create VPC, Subnet, and Security Group
    vpc_id, subnet_id = deployer.create_vpc_and_subnet()
    security_group_id = deployer.create_security_group(vpc_id)
    
    master_instance = None
    
    # Deploy Master Node
    if deploy_master:
        master_deployer = MasterNodeDeployer(region)
        master_instance = master_deployer.deploy_master_node(
            security_group_id, 
            subnet_id, 
            key_name, 
            instance_type
        )
        print("\nAWS master node deployment complete!")
    
    # Deploy Worker Nodes
    if deploy_workers:
        if not deploy_master:
            proceed = input("You're deploying workers without deploying a master. Are you sure? (yes/no): ").strip().lower()
            if proceed != "yes":
                print("Worker deployment cancelled.")
                return {"provider": "aws", "status": "master_only"}
        
        worker_deployer = WorkerNodesDeployer(region)
        worker_deployer.deploy_worker_nodes(
            security_group_id, 
            subnet_id, 
            key_name, 
            num_workers, 
            instance_type
        )
        print("\nAWS worker nodes deployment complete!")
    
    return {"provider": "aws", "vpc_id": vpc_id, "subnet_id": subnet_id}

def main():
    """Main entry point for the unified K8s deployer"""
    parser = argparse.ArgumentParser(description="Deploy Kubernetes clusters on Azure or AWS")
    parser.add_argument(
        "--provider", 
        type=str, 
        default=os.environ.get("CLOUD_PROVIDER", "azure"),
        choices=["azure", "aws"],
        help="Cloud provider to use (azure or aws)"
    )
    parser.add_argument(
        "--component",
        type=str,
        default="all",
        choices=["all", "master", "workers"],
        help="Component to deploy (all, master, or workers)"
    )
    
    args = parser.parse_args()
    
    # Determine what to deploy
    deploy_master = args.component in ["all", "master"]
    deploy_workers = args.component in ["all", "workers"]
    
    try:
        if args.provider.lower() == "azure":
            if deploy_master and deploy_workers:
                result = deploy_azure_cluster(deploy_workers=True)
            elif deploy_master:
                result = deploy_azure_cluster(deploy_workers=False)
            else:  # workers only
                print("=== Deploying Azure Worker Nodes Only ===")
                # Load configuration
                from azure.kubernetes_deployer import load_config
                from azure.worker_nodes import WorkerNodesDeployer
                
                config = load_config()
                join_token = input("Enter the Kubernetes join token (from the head node): ").strip()
                
                # Create worker nodes deployer
                worker_deployer = WorkerNodesDeployer(
                    config['tenant_id'], 
                    config['client_id'], 
                    config['client_secret'], 
                    config['subscription_id']
                )
                
                # Deploy worker nodes
                worker_deployer.create_worker_nodes(
                    config['resource_group_name'],
                    config['vmss_name'],
                    config['location'],
                    config['worker_node_size'],
                    config['worker_node_count'],
                    config['vnet_name'],
                    config['subnet_name'],
                    join_token,
                    config['admin_username'],
                    config['admin_password']
                )
                
                result = {"provider": "azure", "component": "workers_only"}
                print("\nAzure worker nodes deployment complete!")
                
        elif args.provider.lower() == "aws":
            result = deploy_aws_cluster(deploy_master=deploy_master, deploy_workers=deploy_workers)
        else:
            print(f"Unsupported provider: {args.provider}")
            return
            
        print("\n=== Deployment Summary ===")
        for key, value in result.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"\n❌ Error during deployment: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()