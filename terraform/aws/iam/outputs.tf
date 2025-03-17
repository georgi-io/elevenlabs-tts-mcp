output "deployment_role_arn" {
  description = "ARN of the GitHub Actions deployment role"
  value       = aws_iam_role.github_actions_role.arn
}

output "deployment_role_name" {
  description = "Name of the GitHub Actions deployment role"
  value       = aws_iam_role.github_actions_role.name
}

output "github_oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider"
  value       = local.github_oidc_provider_arn
} 