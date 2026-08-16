variable "aws_region" {
  description = "AWS region where the EKS control plane is created."
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
  default     = "astera-production"
}

variable "kubernetes_version" {
  description = "EKS Kubernetes version."
  type        = string
  default     = "1.30"
}

variable "private_subnet_ids" {
  description = "Existing private subnet IDs for the EKS control plane and nodes."
  type        = list(string)
}

variable "cluster_role_arn" {
  description = "Existing IAM role ARN for the EKS control plane."
  type        = string
  sensitive   = true
}

variable "node_role_arn" {
  description = "Existing IAM role ARN for managed node groups."
  type        = string
  sensitive   = true
}

variable "node_instance_types" {
  description = "EC2 instance types for the initial managed node group."
  type        = list(string)
  default     = ["t3.medium"]
}
