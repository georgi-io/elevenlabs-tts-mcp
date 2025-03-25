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

output "api_target_group_arn" {
  description = "ARN of the ALB target group for the API"
  value       = module.ecs.api_target_group_arn
}

output "api_listener_rule_arn" {
  description = "ARN of the ALB listener rule for the API"
  value       = module.ecs.api_listener_rule_arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for ECS service"
  value       = module.ecs.cloudwatch_log_group_name
}

# API Gateway outputs
# Diese Outputs sind nicht mehr verfügbar, da die Route nicht mehr über Terraform verwaltet wird
# output "api_route_key" {
#   description = "Route key for the API Gateway API route"
#   value       = module.api_gateway.api_route_key
# }

# output "api_route_id" {
#   description = "ID of the API Gateway route"
#   value       = module.api_gateway.api_route_id
# }

output "api_endpoint" {
  description = "API endpoint for Jessica"
  value       = "https://api.run.georgi.io/jessica-service"
}

output "mcp_endpoint" {
  description = "MCP server endpoint for Jessica"
  value       = "https://api.run.georgi.io/jessica-service/sse"
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

# SSM Parameter outputs
output "ssm_parameter_names" {
  description = "SSM Parameter names for Jessica service"
  value = {
    base_path = aws_ssm_parameter.jessica_base_path.name
    api_url   = aws_ssm_parameter.jessica_api_url.name
    host      = aws_ssm_parameter.jessica_host.name
    port      = aws_ssm_parameter.jessica_port.name
    debug     = aws_ssm_parameter.jessica_debug.name
    eleven_labs_api_key = aws_ssm_parameter.jessica_eleven_labs_api_key.name
  }
}

output "ssm_parameter_arns" {
  description = "SSM Parameter ARNs for Jessica service"
  value = {
    base_path = aws_ssm_parameter.jessica_base_path.arn
    api_url   = aws_ssm_parameter.jessica_api_url.arn
    host      = aws_ssm_parameter.jessica_host.arn
    port      = aws_ssm_parameter.jessica_port.arn
    debug     = aws_ssm_parameter.jessica_debug.arn
    eleven_labs_api_key = aws_ssm_parameter.jessica_eleven_labs_api_key.arn
  }
} 