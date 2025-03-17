# Find existing GitHub OIDC Provider if ARN is not provided
data "aws_iam_openid_connect_provider" "github_existing" {
  count = var.github_oidc_provider_arn == "" ? 1 : 0
  url   = "https://token.actions.githubusercontent.com"
}

locals {
  github_oidc_provider_arn = var.github_oidc_provider_arn != "" ? var.github_oidc_provider_arn : (
    length(data.aws_iam_openid_connect_provider.github_existing) > 0 ? data.aws_iam_openid_connect_provider.github_existing[0].arn : ""
  )
  
  # Define the GitHub OIDC subject conditions for allowed repositories and branches
  allowed_subjects = [
    for branch in var.allowed_branches : 
    "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/${branch}"
  ]
}

# Deployment role that GitHub Actions can assume
resource "aws_iam_role" "github_actions_role" {
  name = var.role_name
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = local.github_oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = local.allowed_subjects
          }
        }
      }
    ]
  })
  
  tags = {
    Description = "Role for GitHub Actions to build and push Docker images to ECR"
  }
}

# Policy to allow pushing to ECR
resource "aws_iam_policy" "ecr_deployment_policy" {
  name        = "${var.role_name}-policy"
  description = "Policy allowing GitHub Actions to push to ECR"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:GetAuthorizationToken"
        ]
        Resource = var.ecr_repository_arns
      },
      {
        Effect = "Allow"
        Action = "ecr:GetAuthorizationToken"
        Resource = "*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "github_actions_ecr_policy_attachment" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = aws_iam_policy.ecr_deployment_policy.arn
} 