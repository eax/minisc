import boto3
import time
import argparse
import sys
import os
import paramiko


class KubernetesCluster:
    def __init__(self, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.master_instance = None
        self.worker_instances = []
        
        # Read user data scripts from scripts/ directory
        script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
        try:
            with open(os.path.join(script_dir, 'master_init.sh'), 'r') as f:
                self.master_user_data = f.read()
            with open(os.path.join(script_dir, 'worker_init.sh'), 'r') as f:
                self.worker_user_data = f.read()
        except FileNotFoundError as e:
            print(f"Error: Required script files not found: {e}")
            sys.exit(1)

    def create_vpc(self):
        try:
            # Create VPC
            vpc_response = self.ec2.create_vpc(
                CidrBlock='10.0.0.0/16',
                TagSpecifications=[
                    {
                        'ResourceType': 'vpc',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'kubernetes-vpc'
                            }
                        ]
                    }
                ]
            )
            vpc_id = vpc_response['Vpc']['VpcId']

            # Wait for VPC to be available
            waiter = self.ec2.get_waiter('vpc_available')
            waiter.wait(VpcIds=[vpc_id])

            # Enable DNS hostnames
            self.ec2.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsHostnames={'Value': True}
            )

            # Create Internet Gateway
            igw_response = self.ec2.create_internet_gateway()
            igw_id = igw_response['InternetGateway']['InternetGatewayId']

            # Attach Internet Gateway to VPC
            self.ec2.attach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id
            )

            # Create subnet
            subnet_response = self.ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock='10.0.1.0/24',
                TagSpecifications=[
                    {
                        'ResourceType': 'subnet',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'kubernetes-subnet'
                            }
                        ]
                    }
                ]
            )
            subnet_id = subnet_response['Subnet']['SubnetId']

            # Create route table
            route_table_response = self.ec2.create_route_table(VpcId=vpc_id)
            route_table_id = route_table_response['RouteTable']['RouteTableId']

            # Create route to Internet Gateway
            self.ec2.create_route(
                RouteTableId=route_table_id,
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=igw_id
            )

            # Associate route table with subnet
            self.ec2.associate_route_table(
                RouteTableId=route_table_id,
                SubnetId=subnet_id
            )

            return vpc_id, subnet_id

        except Exception as e:
            print(f"Error creating VPC: {str(e)}")
            return None, None

    def create_security_group(self, vpc_id):
        # Create security group for K8s cluster
        try:
            response = self.ec2.create_security_group(
                GroupName='kubernetes-sg',
                Description='Security group for Kubernetes cluster',
                VpcId=vpc_id
            )
            security_group_id = response['GroupId']

            # Add inbound rules
            self.ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': '-1',  # All protocols
                        'FromPort': -1,
                        'ToPort': -1,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            return security_group_id
        except Exception as e:
            print(f"Error creating security group: {str(e)}")
            return None

    def launch_instances(self, security_group_id, subnet_id, instance_type='t2.medium',
                         key_name='your-key-pair', num_workers=2):
        # Get latest Amazon Linux 2 AMI
        response = self.ec2.describe_images(
            Filters=[
                {
                    'Name': 'name',
                    'Values': ['amzn2-ami-hvm-*-x86_64-gp2']
                },
                {
                    'Name': 'state',
                    'Values': ['available']
                }
            ],
            Owners=['amazon']
        )
        ami_id = sorted(response['Images'],
                        key=lambda x: x['CreationDate'],
                        reverse=True)[0]['ImageId']

        # Launch master node
        master_response = self.ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[security_group_id],
            SubnetId=subnet_id,
            UserData=self.get_master_user_data(),
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'k8s-master'
                        }
                    ]
                }
            ]
        )
        self.master_instance = master_response['Instances'][0]

        # Launch worker nodes
        worker_response = self.ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            MinCount=num_workers,
            MaxCount=num_workers,
            SecurityGroupIds=[security_group_id],
            SubnetId=subnet_id,
            UserData=self.get_worker_user_data(),
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'k8s-worker'
                        }
                    ]
                }
            ]
        )
        self.worker_instances = worker_response['Instances']

    def get_master_user_data(self):
        return self.master_user_data

    def get_worker_user_data(self):
        return self.worker_user_data

    def wait_for_instances(self):
        instance_ids = [self.master_instance['InstanceId']] + \
            [instance['InstanceId'] for instance in self.worker_instances]

        waiter = self.ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=instance_ids)

    def cleanup_resources(self):
        try:
            # Terminate instances
            instance_ids = []
            if self.master_instance:
                instance_ids.append(self.master_instance['InstanceId'])
            if self.worker_instances:
                instance_ids.extend([i['InstanceId']
                                    for i in self.worker_instances])

            if instance_ids:
                print("Terminating instances...")
                self.ec2.terminate_instances(InstanceIds=instance_ids)
                waiter = self.ec2.get_waiter('instance_terminated')
                waiter.wait(InstanceIds=instance_ids)

            # Get VPC ID from tags
            vpcs = self.ec2.describe_vpcs(
                Filters=[
                    {
                        'Name': 'tag:Name',
                        'Values': ['kubernetes-vpc']
                    }
                ]
            )['Vpcs']

            if not vpcs:
                print("No VPC found to clean up")
                return

            vpc_id = vpcs[0]['VpcId']

            # Delete security groups
            security_groups = self.ec2.describe_security_groups(
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [vpc_id]
                    },
                    {
                        'Name': 'group-name',
                        'Values': ['kubernetes-sg']
                    }
                ]
            )['SecurityGroups']

            for sg in security_groups:
                print(f"Deleting security group: {sg['GroupId']}")
                self.ec2.delete_security_group(GroupId=sg['GroupId'])

            # Get and delete subnets
            subnets = self.ec2.describe_subnets(
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [vpc_id]
                    }
                ]
            )['Subnets']

            # Delete route table associations
            for subnet in subnets:
                route_tables = self.ec2.describe_route_tables(
                    Filters=[
                        {
                            'Name': 'vpc-id',
                            'Values': [vpc_id]
                        }
                    ]
                )['RouteTables']

                for rt in route_tables:
                    for assoc in rt.get('Associations', []):
                        if assoc.get('SubnetId') == subnet['SubnetId']:
                            print(
                                f"Deleting route table association: {assoc['RouteTableAssociationId']}")
                            self.ec2.disassociate_route_table(
                                AssociationId=assoc['RouteTableAssociationId']
                            )

            # Delete route tables (except main)
            route_tables = self.ec2.describe_route_tables(
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [vpc_id]
                    }
                ]
            )['RouteTables']

            for rt in route_tables:
                if not rt.get('Associations', []) or not rt['Associations'][0].get('Main', False):
                    print(f"Deleting route table: {rt['RouteTableId']}")
                    self.ec2.delete_route_table(
                        RouteTableId=rt['RouteTableId'])

            # Detach and delete internet gateway
            igws = self.ec2.describe_internet_gateways(
                Filters=[
                    {
                        'Name': 'attachment.vpc-id',
                        'Values': [vpc_id]
                    }
                ]
            )['InternetGateways']

            for igw in igws:
                print(
                    f"Detaching and deleting internet gateway: {igw['InternetGatewayId']}")
                self.ec2.detach_internet_gateway(
                    InternetGatewayId=igw['InternetGatewayId'],
                    VpcId=vpc_id
                )
                self.ec2.delete_internet_gateway(
                    InternetGatewayId=igw['InternetGatewayId']
                )

            # Delete subnets
            for subnet in subnets:
                print(f"Deleting subnet: {subnet['SubnetId']}")
                self.ec2.delete_subnet(SubnetId=subnet['SubnetId'])

            # Finally, delete the VPC
            print(f"Deleting VPC: {vpc_id}")
            self.ec2.delete_vpc(VpcId=vpc_id)

            print("Cleanup completed successfully")

        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    def setup_helm_charts(self, key_name):
        """Install and configure common Helm charts"""
        try:
            # Setup SSH client
            key_path = os.path.expanduser(f'~/.ssh/{key_name}.pem')
            if not os.path.exists(key_path):
                print(f"Error: Key file not found at {key_path}")
                return False

            k = paramiko.RSAKey.from_private_key_file(key_path)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Get master node's public IP
            master_info = self.ec2.describe_instances(
                InstanceIds=[self.master_instance['InstanceId']]
            )['Reservations'][0]['Instances'][0]
            master_ip = master_info['PublicIpAddress']

            # Connect to master node
            print("Connecting to master node to setup Helm charts...")
            ssh.connect(hostname=master_ip, username='ec2-user', pkey=k)

            # Wait for Helm to be ready
            print("Waiting for Helm to be ready...")
            for _ in range(12):  # Try for 2 minutes
                _, stdout, _ = ssh.exec_command('helm version')
                if stdout.channel.recv_exit_status() == 0:
                    break
                time.sleep(10)
            else:
                print("Timeout waiting for Helm to be ready")
                return False

            # Add repositories
            print("Adding Helm repositories...")
            _, stdout, stderr = ssh.exec_command('helm repo add bitnami https://charts.bitnami.com/bitnami')
            if stdout.channel.recv_exit_status() != 0:
                print(f"Error adding bitnami repo: {stderr.read().decode('utf-8')}")
                return False

            _, stdout, stderr = ssh.exec_command('helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/')
            if stdout.channel.recv_exit_status() != 0:
                print(f"Error adding kubernetes-dashboard repo: {stderr.read().decode('utf-8')}")
                return False

            _, stdout, stderr = ssh.exec_command('helm repo update')
            if stdout.channel.recv_exit_status() != 0:
                print(f"Error updating repos: {stderr.read().decode('utf-8')}")
                return False

            # Install common charts
            charts_to_install = [
                {
                    'name': 'metrics-server',
                    'repo': 'bitnami',
                    'chart': 'metrics-server',
                    'namespace': 'kube-system'
                },
                {
                    'name': 'nginx-ingress',
                    'repo': 'bitnami',
                    'chart': 'nginx-ingress-controller',
                    'namespace': 'ingress-nginx',
                    'create_namespace': True
                },
                {
                    'name': 'prometheus',
                    'repo': 'bitnami',
                    'chart': 'kube-prometheus',
                    'namespace': 'monitoring',
                    'create_namespace': True
                },
                {
                    'name': 'kubernetes-dashboard',
                    'repo': 'kubernetes-dashboard',
                    'chart': 'kubernetes-dashboard',
                    'namespace': 'kubernetes-dashboard',
                    'create_namespace': True
                }
            ]

            for chart in charts_to_install:
                namespace = chart['namespace']
                if chart.get('create_namespace', False):
                    print(f"Creating namespace {namespace}...")
                    _, stdout, stderr = ssh.exec_command(f'kubectl create namespace {namespace}')
                    if stdout.channel.recv_exit_status() != 0:
                        print(f"Error creating namespace {namespace}: {stderr.read().decode('utf-8')}")
                        continue
                
                print(f"Installing {chart['name']}...")
                cmd = f"helm install {chart['name']} {chart['repo']}/{chart['chart']} --namespace {namespace}"
                _, stdout, stderr = ssh.exec_command(cmd)
                if stdout.channel.recv_exit_status() != 0:
                    print(f"Error installing {chart['name']}: {stderr.read().decode('utf-8')}")
                else:
                    print(f"Successfully installed {chart['name']}")

            # Verify installations
            print("\nVerifying Helm installations...")
            _, stdout, stderr = ssh.exec_command('helm list -A')
            if stdout.channel.recv_exit_status() == 0:
                print(stdout.read().decode('utf-8'))
            else:
                print(f"Error listing Helm releases: {stderr.read().decode('utf-8')}")

            ssh.close()
            return True

        except Exception as e:
            print(f"Error setting up Helm charts: {str(e)}")
            return False

    def get_cluster_info(self, key_name):
        """Get cluster information including Helm releases"""
        try:
            key_path = os.path.expanduser(f'~/.ssh/{key_name}.pem')
            k = paramiko.RSAKey.from_private_key_file(key_path)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            master_info = self.ec2.describe_instances(
                InstanceIds=[self.master_instance['InstanceId']]
            )['Reservations'][0]['Instances'][0]
            master_ip = master_info['PublicIpAddress']

            ssh.connect(hostname=master_ip, username='ec2-user', pkey=k)

            print("\nCluster Information:")
            print("-" * 50)
            
            print("\nNodes:")
            _, stdout, _ = ssh.exec_command('kubectl get nodes')
            print(stdout.read().decode('utf-8'))

            print("\nHelm Releases:")
            _, stdout, _ = ssh.exec_command('helm list -A')
            print(stdout.read().decode('utf-8'))

            print("\nRunning Pods:")
            _, stdout, _ = ssh.exec_command('kubectl get pods -A')
            print(stdout.read().decode('utf-8'))

            ssh.close()
            return True

        except Exception as e:
            print(f"Error getting cluster information: {str(e)}")
            return False


def print_menu():
    print("\nKubernetes Cluster Manager")
    print("1. Deploy cluster")
    print("2. Clean up resources")
    print("3. Show cluster status")
    print("4. Install/Update Helm charts")
    print("5. Show detailed cluster info")
    print("6. Exit")
    return input("Select an option (1-6): ")


def main():
    parser = argparse.ArgumentParser(
        description='Deploy or manage Kubernetes cluster on AWS')
    parser.add_argument('--key-name', required=True,
                        help='Name of the EC2 key pair to use')
    parser.add_argument('--region', default='us-east-1',
                        help='AWS region (default: us-east-1)')
    parser.add_argument('--workers', type=int, default=2,
                        help='Number of worker nodes (default: 2)')
    parser.add_argument('--instance-type', default='t2.medium',
                        help='EC2 instance type (default: t2.medium)')

    args = parser.parse_args()

    # Initialize the cluster
    cluster = KubernetesCluster(region=args.region)

    while True:
        choice = print_menu()

        try:
            if choice == '1':  # Deploy
                print("\nDeploying Kubernetes cluster...")
                # Create VPC and subnet
                vpc_id, subnet_id = cluster.create_vpc()
                if not vpc_id or not subnet_id:
                    continue

                # Create security group
                security_group_id = cluster.create_security_group(vpc_id)
                if not security_group_id:
                    continue

                # Launch instances
                cluster.launch_instances(
                    security_group_id=security_group_id,
                    subnet_id=subnet_id,
                    key_name=args.key_name,
                    instance_type=args.instance_type,
                    num_workers=args.workers
                )

                # Wait for instances to be running
                cluster.wait_for_instances()

                print("\nKubernetes cluster has been provisioned!")
                print(
                    f"Master node ID: {cluster.master_instance['InstanceId']}")
                print("Worker node IDs:", [instance['InstanceId']
                      for instance in cluster.worker_instances])

                print("\nSetting up Helm charts...")
                if cluster.setup_helm_charts(args.key_name):
                    print("Helm charts installed successfully!")
                else:
                    print("Failed to install some Helm charts. Please check the logs.")

            elif choice == '2':  # Clean up
                confirm = input(
                    "\nAre you sure you want to clean up all resources? (yes/no): ")
                if confirm.lower() == 'yes':
                    print("\nCleaning up resources...")
                    cluster.cleanup_resources()
                else:
                    print("\nCleanup cancelled.")

            elif choice == '3':  # Show status
                try:
                    if cluster.master_instance:
                        master_id = cluster.master_instance['InstanceId']
                        master_status = cluster.ec2.describe_instances(
                            InstanceIds=[master_id]
                        )['Reservations'][0]['Instances'][0]['State']['Name']
                        print(f"\nMaster node ({master_id}): {master_status}")

                    if cluster.worker_instances:
                        worker_ids = [instance['InstanceId']
                                      for instance in cluster.worker_instances]
                        workers_status = cluster.ec2.describe_instances(
                            InstanceIds=worker_ids
                        )['Reservations'][0]['Instances']

                        print("\nWorker nodes:")
                        for worker in workers_status:
                            print(
                                f"- {worker['InstanceId']}: {worker['State']['Name']}")

                    if not cluster.master_instance and not cluster.worker_instances:
                        print("\nNo active cluster found.")

                except Exception as e:
                    print("\nNo active cluster found or error fetching status.")

            elif choice == '4':  # Install/Update Helm charts
                if not cluster.master_instance:
                    print("\nNo active cluster found. Please deploy a cluster first.")
                    continue
                    
                print("\nInstalling/Updating Helm charts...")
                if cluster.setup_helm_charts(args.key_name):
                    print("Helm charts installed/updated successfully!")
                else:
                    print("Failed to install/update Helm charts. Please check the logs.")

            elif choice == '5':  # Show detailed cluster info
                if not cluster.master_instance:
                    print("\nNo active cluster found. Please deploy a cluster first.")
                    continue
                    
                cluster.get_cluster_info(args.key_name)

            elif choice == '6':  # Exit
                confirm = input(
                    "\nAre you sure you want to exit? Any running resources will continue to incur costs (yes/no): ")
                if confirm.lower() == 'yes':
                    print("\nExiting... Remember to clean up resources if you're done!")
                    break

            else:
                print("\nInvalid option. Please try again.")

        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
        print("Remember to clean up resources if you're done!")
        sys.exit(0)
