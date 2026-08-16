output "cluster_name" {
  description = "EKS cluster name for kubeconfig and deployment automation."
  value       = aws_eks_cluster.astera.name
}

output "cluster_endpoint" {
  description = "Private EKS API endpoint."
  value       = aws_eks_cluster.astera.endpoint
  sensitive   = true
}

output "cluster_certificate_authority" {
  description = "EKS certificate authority data."
  value       = aws_eks_cluster.astera.certificate_authority[0].data
  sensitive   = true
}
