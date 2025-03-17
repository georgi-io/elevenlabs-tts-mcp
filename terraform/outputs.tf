output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = module.ecr.repository_url
}

output "ecr_repository_name" {
  description = "The name of the ECR repository"
  value       = module.ecr.repository_name
}

output "ecr_repository_arn" {
  description = "The ARN of the ECR repository"
  value       = module.ecr.repository_arn
}

output "ecr_registry_id" {
  description = "The registry ID where the repository was created"
  value       = module.ecr.registry_id
}

output "github_actions_deployment_role_arn" {
  description = "ARN of the IAM role for GitHub Actions deployment"
  value       = module.iam.deployment_role_arn
}

output "github_actions_deployment_role_name" {
  description = "Name of the IAM role for GitHub Actions deployment"
  value       = module.iam.deployment_role_name
}

output "github_oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider for authentication"
  value       = module.iam.github_oidc_provider_arn
}

# Central infrastructure outputs that might be useful for this service
output "vpc_id" {
  description = "The ID of the VPC from central infrastructure"
  value       = data.terraform_remote_state.infrastructure.outputs.vpc_id
}

output "private_subnet_ids" {
  description = "The IDs of the private subnets from central infrastructure"
  value       = data.terraform_remote_state.infrastructure.outputs.private_subnet_ids
}

output "api_gateway_id" {
  description = "The ID of the API Gateway from central infrastructure"
  value       = data.terraform_remote_state.infrastructure.outputs.api_gateway_id
} 