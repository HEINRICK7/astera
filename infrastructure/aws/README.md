# Astera AWS / EKS blueprint

This Terraform root creates the EKS control plane and the initial managed
Runtime node group. It intentionally receives private subnets and IAM role
ARNs as variables; AWS credentials, IAM roles, VPCs and state backends are
managed outside this repository.

```bash
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

The private-only endpoint requires deployment automation or an operator path
with network access to the VPC.
