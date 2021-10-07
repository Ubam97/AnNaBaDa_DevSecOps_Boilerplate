# 사전 설치

```bash
sudo yum install -y yum-utils
sudo yum install -y terraform
sudo yum install -y git

# eksctl 설치
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
# 버전 확인
eksctl version

# kubectl 설치
curl -o kubectl https://amazon-eks.s3-us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/kubectl
chmod +x ./kubectl
# kubectl 바이너리 파일을 적절한 디렉토리에 옮기고 path 지정.
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$HOME/bin:$PATH
# bash profile 에 적용
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
# 버전 확인
kubectl version --short --client

# amazon linux는 설치필요 x
aws configure
AWS Access Key ID : 사용자의 값 입력
AWS Secret Access Key :
Default region name :
Default output format :

# terraform-eks가 있는 github Clone
git clone https://github.com/eub456/AnNaBaDa_DevSecOps_Boilerplate.git

# terraform 실행 (실행하는 곳이 마스터 노드역할)
terraform init # 초기화
terraform plan # 만들 리소스 확인
terraform apply # 리소스 생성(15~20분 소요)

# aws-iam-authenticator 설치
curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/linux/amd64/aws-iam-authenticator
# 권한 설정
chmod +x ./aws-iam-authenticator
# Path 설정
mkdir -p $HOME/bin && cp ./aws-iam-authenticator $HOME/bin/aws-iam-authenticator && export PATH=$HOME/bin:$PATH
# 환경 변수에 추가
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc

# 인증된 사용자를 이용하여 token을 가져옴
aws-iam-authenticator token -i {클러스터 이름} | python2 -m json.tool # python3버전이 있다면 python3로 가능
aws eks --region {리전} update-kubeconfig --name {클러스터 이름}

# 확인
kubectl get svc
kubectl get nodes
```

## EKS 구성도

![terraform-eks.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/f2a6a5fc-d5ba-43e9-bb87-3cea99038ffa/terraform-eks.png)

마스터 노드는 기본 VPC에 생성하여 위에서 설치한 파일들을 설치합니다. (다른 VPC에 설치하여 가능)

워커 노드는 EKS Cluster를 위한 네트워크를 생성하고 가용영역(a, b, c)에 인스턴스를 하나씩 구성하였습니다. (가용영역(d)는 제외하였음)

### provider.tf

provider는 어떤 모듈을 구현할지 선언하고 모듈 내부의 기능을 구현합니다. 필요한 모듈은 아래에 접속하여 찾아보면 됩니다. [https://registry.terraform.io/](https://registry.terraform.io/)

### workstation-external-ip.tf

Kubernetes 클러스터에 대한 인바운드 EC2 Security Group 액세스를 구성하기 위해 로컬 워크스테이션의 외부 IP를 쉽게 가져오기 위한 예제로만 제공됩니다.

### variables.tf

리소스 구성을 위해 변수를 지정한 파일입니다.

### vpc.tf

네트워크(VPC, Subnet, IGW, RouteTable 등) 관련 리소스를 모아놓은 파일입니다. 

### eks-cluster.tf

IAM Role, Policy, Security Group, Cluster를 생성하는 파일입니다.

### eks-worker-nodes.tf

 노드 그룹을 만들어 위에서 만든 클러스터와 연결하는 파일입니다.
