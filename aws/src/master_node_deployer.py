import os
import sys
import paramiko
import time
from string import Template
from .kubernetes_deployer import KubernetesDeployer


class MasterNodeDeployer(KubernetesDeployer):
    def __init__(self, region='us-east-1'):
        super().__init__(region)
        self.master_instance = None

    def deploy_master_node(self, security_group_id, subnet_id, key_name, instance_type='t2.medium'):
        try:
            # Load cloud-init YAML template
            template_path = os.path.join(os.path.dirname(__file__), '../templates/cloud-init_head_node.yaml')
            with open(template_path, 'r') as f:
                template = Template(f.read())
                user_data = template.substitute()

            # Get latest Amazon Linux 2 AMI
            response = self.ec2.describe_images(
                Filters=[
                    {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                    {'Name': 'state', 'Values': ['available']}
                ],
                Owners=['amazon']
            )
            ami_id = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)[0]['ImageId']

            # Launch Master Node
            master_response = self.ec2.run_instances(
                ImageId=ami_id,
                InstanceType=instance_type,
                KeyName=key_name,
                MinCount=1,
                MaxCount=1,
                SecurityGroupIds=[security_group_id],
                SubnetId=subnet_id,
                UserData=user_data,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [{'Key': 'Name', 'Value': 'k8s-master'}]
                    }
                ]
            )
            self.master_instance = master_response['Instances'][0]
            print(f"Master node launched: {self.master_instance['InstanceId']}")
        except Exception as e:
            print(f"Error deploying Master Node: {str(e)}")
            sys.exit(1)

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