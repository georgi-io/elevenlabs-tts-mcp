output "service_name" {
  description = "ECS Service name"
  value       = aws_ecs_service.service.name
}

output "service_id" {
  description = "ECS Service ID"
  value       = aws_ecs_service.service.id
}

output "container_port" {
  description = "Container port for the main API"
  value       = var.container_port
}

output "task_definition_arn" {
  description = "ARN of the task definition"
  value       = aws_ecs_task_definition.service.arn
}

output "task_definition_family" {
  description = "Family of the task definition"
  value       = aws_ecs_task_definition.service.family
}

output "security_group_id" {
  description = "ID of the security group used by the ECS service"
  value       = aws_security_group.service.id
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.service.name
}

output "task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

output "execution_role_arn" {
  description = "ARN of the ECS execution role"
  value       = aws_iam_role.ecs_execution.arn
}

output "api_target_group_arn" {
  description = "ARN of the ALB target group for the API"
  value       = aws_lb_target_group.api.arn
}

output "api_listener_rule_arn" {
  description = "ARN of the ALB listener rule for the API"
  value       = aws_lb_listener_rule.api_https.arn
} 