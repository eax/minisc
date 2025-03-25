#!/bin/bash
# Install required packages
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker

# Install kubectl, kubelet, and kubeadm
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF

yum install -y kubelet kubeadm kubectl
systemctl start kubelet
systemctl enable kubelet

# Initialize the master node
kubeadm init --pod-network-cidr=192.168.0.0/16

# Set up kubectl for the root user
export KUBECONFIG=/etc/kubernetes/admin.conf
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config

# Install Calico network plugin
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# Install Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# Initialize Helm and add common repositories
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update 