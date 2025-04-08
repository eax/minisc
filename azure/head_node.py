import base64
from string import Template
from .kubernetes_deployer import KubernetesDeployer

class HeadNodeDeployer(KubernetesDeployer):
    def create_kubernetes_head_node(self, group_name, vm_name, location, vm_size, vnet_name, subnet_name, admin_username, admin_password):
        # Ensure VNet and subnet exist
        self._ensure_network_exists(group_name, location, vnet_name, subnet_name)
        
        # Get subnet ID
        subnet = self.network_client.subnets.get(group_name, vnet_name, subnet_name)
        
        # Create public IP
        public_ip_name = f"{vm_name}-ip"
        public_ip = self.network_client.public_ip_addresses.begin_create_or_update(
            group_name,
            public_ip_name,
            {
                "location": location,
                "sku": {"name": "Standard"},
                "public_ip_allocation_method": "Static"
            }
        ).result()
        print(f"Public IP '{public_ip_name}' created.")
        
        # Create NIC
        nic_name = f"{vm_name}-nic"
        nic = self.network_client.network_interfaces.begin_create_or_update(
            group_name,
            nic_name,
            {
                "location": location,
                "ip_configurations": [
                    {
                        "name": "ipconfig",
                        "subnet": {"id": subnet.id},
                        "public_ip_address": {"id": public_ip.id}
                    }
                ]
            }
        ).result()
        print(f"Network interface '{nic_name}' created.")

        # Load and render cloud-init template
        with open("../templates/cloud_init_head_node.yaml", "r") as file:
            template = Template(file.read())
            cloud_init_script = template.substitute(
                POD_NETWORK_CIDR="10.244.0.0/16",
                ADMIN_USERNAME=admin_username,
                FLANNEL_URL="https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml"
            )

        # Create VM
        vm_params = {
            'location': location,
            'hardware_profile': {
                'vm_size': vm_size
            },
            'storage_profile': {
                'image_reference': {
                    'publisher': 'Canonical',
                    'offer': 'UbuntuServer',
                    'sku': '24_04-lts',
                    'version': 'latest'
                },
                'os_disk': {
                    'create_option': 'FromImage',
                    'managed_disk': {
                        'storage_account_type': 'Premium_LRS'
                    }
                }
            },
            'os_profile': {
                'computer_name': vm_name,
                'admin_username': admin_username,
                'admin_password': admin_password,
                'custom_data': base64.b64encode(cloud_init_script.encode()).decode()
            },
            'network_profile': {
                'network_interfaces': [
                    {
                        'id': nic.id,
                        'primary': True
                    }
                ]
            }
        }
        
        creation = self.compute_client.virtual_machines.begin_create_or_update(
            group_name, vm_name, vm_params
        )
        vm = creation.result()
        print(f"Kubernetes head node '{vm_name}' created. Installing Kubernetes components...")

        # Retrieve the public IP
        public_ip_info = self.network_client.public_ip_addresses.get(group_name, public_ip_name)
        print(f"Kubernetes head node created with public IP: {public_ip_info.ip_address}")
        print(f"SSH access: ssh {admin_username}@{public_ip_info.ip_address}")
        print("Note: Wait a few minutes for Kubernetes installation to complete.")
        
        return vm, public_ip_info.ip_address