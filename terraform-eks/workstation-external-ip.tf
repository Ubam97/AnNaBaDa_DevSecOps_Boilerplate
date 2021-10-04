#
# Workstation External IP
#
# This configuration is not required and is
# only provided as an example to easily fetch
# the external IP of your local workstation to
# configure inbound EC2 Security Group access
# to the Kubernetes cluster.
#
# 이 구성은 필요하지 않으며 Kubernetes 클러스터에 대한 인바운드 EC2 Security Group 액세스를 구성하기 위해 로컬 워크스테이션의 외부 IP를 쉽게 가져오기 위한 예제로만 제공됩니다.

data "http" "workstation-external-ip" {
  url = "http://ipv4.icanhazip.com"
}

# Override with variable or hardcoded value if necessary
locals {
  workstation-external-cidr = "${chomp(data.http.workstation-external-ip.body)}/32"
}
