# Terraform-EKS

```bash
# Pre-installation
sudo yum install -y yum-utils
sudo yum install -y terraform
sudo yum install -y git

# eksctl installation
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
# Check the version
eksctl version

# Kubectl installation
curl -o kubectl https://amazon-eks.s3-us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/kubectl
chmod +x ./kubectl
# Move kubectl binary file to the appropriate directory and specify path
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$HOME/bin:$PATH
# Apply it to the bash profile
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
# Check the version
kubectl version --short --client

# Amazon Linux needs to be installed x
aws configure
AWS Access Key ID : # Enter user's value
AWS Secret Access Key :
Default region name :
Default output format :

# Clone github with terraform-eks
git clone https://github.com/eub456/AnNaBaDa_DevSecOps_Boilerplate.git

# Run terraform (where it runs acts as a master node)
terraform init # initialization
terraform plan # Check the resources you want to create
terraform apply # resource creation (15-20 minutes)

# Install aws-iam-authenticator
curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/linux/amd64/aws-iam-authenticator
# Permission setting
chmod +x ./aws-iam-authenticator
# Path setting
mkdir -p $HOME/bin && cp ./aws-iam-authenticator $HOME/bin/aws-iam-authenticator && export PATH=$HOME/bin:$PATH
# Add to environmental variables
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc

# Imported token using an authenticated user
aws-iam-authenticator token -i {cluster name} | python2 -m json.tool # python3 version, it can be python3
aws eks --region {region} update-kubeconfig --name {cluster name}

# Checked
kubectl get svc
kubectl get nodes
```

## EKS 구성도

![terraform-eks.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/f2a6a5fc-d5ba-43e9-bb87-3cea99038ffa/terraform-eks.png)

The master node creates on the default VPC and installs the files installed above. (It can be installed on another VPC)

The worker node created a network for the EKS cluster and configured one instance in the available areas (a, b, c). (Available area (d) is excluded)

### provider.tf

The provider declares which module to implement and implements functions inside the module. You can find the necessary modules by connecting them below. [https://registry.terraform.io/](https://registry.terraform.io/)

### workstation-external-ip.tf

To configure inbound EC2 security group access to the Kubernetes cluster, it is provided only as an example to easily import the external IP of the local workstation.

### variables.tf

A file that specifies a variable for resource configuration.

### vpc.tf

It is a file that collects network-related resources (VPC, Subnet, IGW, RouteTable, etc.).

### eks-cluster.tf

Files that create IAM Role, Policy, Security Group, and Cluster.

### eks-worker-nodes.tf

It is a file that creates a node group and connects it to the cluster created above.
