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

# ECS Fargate outputs
output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = module.ecs.service_name
}

output "ecs_service_id" {
  description = "ID of the ECS service"
  value       = module.ecs.service_id
}

output "ecs_task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = module.ecs.task_definition_arn
}

output "ecs_container_port" {
  description = "Port exposed by the container for the API"
  value       = module.ecs.container_port
}

output "ecs_mcp_port" {
  description = "Port exposed by the container for the MCP server"
  value       = module.ecs.mcp_port
}

output "api_target_group_arn" {
  description = "ARN of the ALB target group for the API"
  value       = module.ecs.api_target_group_arn
}

output "mcp_target_group_arn" {
  description = "ARN of the ALB target group for the MCP server"
  value       = module.ecs.mcp_target_group_arn
}

output "api_listener_rule_arn" {
  description = "ARN of the ALB listener rule for the API"
  value       = module.ecs.api_listener_rule_arn
}

output "mcp_listener_rule_arn" {
  description = "ARN of the ALB listener rule for the MCP server"
  value       = module.ecs.mcp_listener_rule_arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for ECS service"
  value       = module.ecs.cloudwatch_log_group_name
}

# API Gateway outputs
output "api_route_key" {
  description = "Route key for the API Gateway API route"
  value       = module.api_gateway.api_route_key
}

output "mcp_route_key" {
  description = "Route key for the API Gateway MCP route"
  value       = module.api_gateway.mcp_route_key
}

output "api_endpoint" {
  description = "API endpoint for Jessica"
  value       = "https://api.run.georgi.io/jessica"
}

output "mcp_endpoint" {
  description = "MCP server endpoint for Jessica"
  value       = "https://api.run.georgi.io/jessica/sse"
}

# Central infrastructure outputs that might be useful for this service
output "vpc_id" {
  description = "ID of the VPC from central infrastructure"
  value       = data.terraform_remote_state.infrastructure.outputs.vpc_id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets from central infrastructure"
  value       = data.terraform_remote_state.infrastructure.outputs.private_subnet_ids
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster from central infrastructure"
  value       = data.terraform_remote_state.infrastructure.outputs.ecs_cluster_arn
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster from central infrastructure"
  value       = data.terraform_remote_state.infrastructure.outputs.ecs_cluster_name
}

output "api_gateway_id" {
  description = "ID of the API Gateway from central infrastructure"
  value       = data.terraform_remote_state.infrastructure.outputs.api_gateway_id
}

output "vpc_link_id" {
  description = "ID of the VPC Link used by API Gateway"
  value       = data.terraform_remote_state.infrastructure.outputs.vpc_link_id
} 