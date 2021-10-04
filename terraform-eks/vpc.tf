resource "aws_vpc" "terraform-eks-vpc" {
  cidr_block = "10.110.0.0/16"

  tags = {
    "Name" = "terraform-eks-vpc"
    "kubernetes.io/cluster/${var.cluster-name}" = "shared"
  }
}


# public subnet
resource "aws_subnet" "terraform-eks-public-subnet" {
  count = 3

  availability_zone       = data.aws_availability_zones.available.names[count.index]
  cidr_block              = "10.110.${count.index+1}.0/24"
  map_public_ip_on_launch = true
  vpc_id                  = aws_vpc.terraform-eks-vpc.id

  tags = {
    #"Name" = "terraform-eks-public-${count.index+1 == 1 ? "a" : "c"}"
    "Name" = "eks-public-${var.availability_zones[count.index]}"
    "kubernetes.io/cluster/${var.cluster-name}" = "shared"
  }
}
#aws_subnet.tags 중에 "kubernetes.io/cluster/${var.cluster-name}" = "shared"가  aws_vpc.tags 와 동일해야 한다. 이게 다를 경우 같은 클러스터인지 인식을 못해 정상적인 네트워크가 형성되지 않는다. 


resource "aws_internet_gateway" "terraform-eks-igw" {
  vpc_id = aws_vpc.terraform-eks-vpc.id

  tags = {
    Name = "terraform-eks-igw"
  }
}


# public route table
resource "aws_route_table" "terraform-eks-public-route" {
  vpc_id = aws_vpc.terraform-eks-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.terraform-eks-igw.id
  }

  tags = {
    "Name" = "terraform-eks-public"
  }
}


# public route table association
resource "aws_route_table_association" "terraform-eks-public-routing" {
  count = 3

  subnet_id      = aws_subnet.terraform-eks-public-subnet.*.id[count.index]
  route_table_id = aws_route_table.terraform-eks-public-route.id
}