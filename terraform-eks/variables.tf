variable "aws_region" {
  default = "ap-northeast-2"
}

variable "cluster-name" {
  default = "terraform-eks"
  type    = string
}

variable "availability_zones" {
  type        = list(string)
  default     = ["a", "b", "c"]
}