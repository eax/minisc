from minisc.azure.kubernetes_deployer import load_config
from minisc.azure.head_node import HeadNodeDeployer
from minisc.azure.worker_nodes import WorkerNodesDeployer

def main():
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
    print("To deploy worker nodes, you will need to:")
    print("1. SSH into the head node")
    print("2. Run: sudo kubeadm token create --print-join-command")
    print("3. Use the output to update the 'join_token' parameter in your configuration\n")
    
    # Prompt user to deploy worker nodes
    deploy_workers = input("Do you want to deploy worker nodes now? (yes/no): ").strip().lower()
    if deploy_workers == "yes":
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
        
        print("\nWorker nodes deployment complete!")
    else:
        print("Worker nodes deployment skipped. You can deploy them later by running this script again.")

if __name__ == "__main__":
    main()