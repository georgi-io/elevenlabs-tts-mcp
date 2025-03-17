variable "role_name" {
  description = "Name of the IAM role for GitHub Actions deployment"
  type        = string
  default     = "github-actions-deployment-role"
}

variable "ecr_repository_arns" {
  description = "List of ECR repository ARNs the role will have access to"
  type        = list(string)
}

variable "github_oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider"
  type        = string
  default     = ""
}

variable "github_org" {
  description = "GitHub organization name"
  type        = string
  default     = "georgi-io"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "jessica"
}

variable "allowed_branches" {
  description = "List of branches allowed to assume the role"
  type        = list(string)
  default     = ["main"]
} 