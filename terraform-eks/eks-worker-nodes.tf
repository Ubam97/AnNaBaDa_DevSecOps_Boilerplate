resource "aws_iam_role" "terraform-eks-node" {
  name = "terraform-eks-node"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "terraform-eks-node-AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.terraform-eks-node.name
}

resource "aws_iam_role_policy_attachment" "terraform-eks-node-AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.terraform-eks-node.name
}

resource "aws_iam_role_policy_attachment" "terraform-eks-node-AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.terraform-eks-node.name
}

# t2 small node group
resource "aws_eks_node_group" "terraform-eks-t2-small" {
  count           = 3
  cluster_name    = aws_eks_cluster.terraform-eks-cluster.name
  node_group_name = "terraform-eks-t2-small"
  node_role_arn   = aws_iam_role.terraform-eks-node.arn
  subnet_ids      = concat(aws_subnet.terraform-eks-public-subnet[*].id)
  instance_types = ["t3.medium"]
  disk_size = 20

  # 기존 aws_subnet.eks-public-subnet[*].id
  # [aws_subnet.public-subnet["a"].id, aws_public-subnet["b"].id, aws_public-subnet["c"].id]

  labels = {
    "role" = "terraform-eks-t2-small"
  }

  scaling_config {
    desired_size = 3
    min_size     = 1
    max_size     = 4
  }

  remote_access {
    ec2_ssh_key = "pro1"
  }

  depends_on = [
    aws_iam_role_policy_attachment.terraform-eks-node-AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.terraform-eks-node-AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.terraform-eks-node-AmazonEC2ContainerRegistryReadOnly,
  ]

  tags = {
    "Name" = "${aws_eks_cluster.terraform-eks-cluster.name}-terraform-eks-t2-small-${count.index+1}"
  }
}