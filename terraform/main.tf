terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "georgi-io-terraform-state"
    key    = "services/jessica/terraform.tfstate"
    region = "eu-central-1"
  }

  required_version = ">= 1.0.0"
}

provider "aws" {
  region = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      Service     = "jessica"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Helper data resources
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# Import central infrastructure outputs
data "terraform_remote_state" "infrastructure" {
  backend = "s3"
  config = {
    bucket = "georgi-io-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "eu-central-1"
    profile = var.aws_profile
  }
}

# SSM Parameter Store for environment variables
resource "aws_ssm_parameter" "jessica_base_path" {
  name        = "/jessica/${var.environment}/base-path"
  description = "Base path for Jessica service"
  type        = "String"
  value       = "jessica-service"
  
  tags = {
    Environment = var.environment
    Service     = "jessica"
  }
}

resource "aws_ssm_parameter" "jessica_root_path" {
  name        = "/jessica/${var.environment}/root-path"
  description = "ROOT_PATH for Jessica service (with leading slash)"
  type        = "String"
  value       = "/jessica-service"
  
  tags = {
    Environment = var.environment
    Service     = "jessica"
  }
}

resource "aws_ssm_parameter" "jessica_api_url" {
  name        = "/jessica/${var.environment}/api-url"
  description = "API URL for Jessica service"
  type        = "String"
  value       = "https://api.run.georgi.io/jessica-service"
  
  tags = {
    Environment = var.environment
    Service     = "jessica"
  }
}

# For sensitive data use SecureString
resource "aws_ssm_parameter" "jessica_eleven_labs_api_key" {
  name        = "/jessica/${var.environment}/eleven-labs-api-key"
  description = "Eleven Labs API Key for voice synthesis"
  type        = "SecureString"
  value       = var.eleven_labs_api_key != "" ? var.eleven_labs_api_key : "PLACE_REAL_KEY_IN_AWS_CONSOLE"
  overwrite   = true
  
  lifecycle {
    ignore_changes = [value]
  }
  
  tags = {
    Environment = var.environment
    Service     = "jessica"
  }
}

# Zusätzliche Environment-Variablen als SSM Parameter
resource "aws_ssm_parameter" "jessica_host" {
  name        = "/jessica/${var.environment}/host"
  description = "Host configuration for Jessica service"
  type        = "String"
  value       = "0.0.0.0"
  
  tags = {
    Environment = var.environment
    Service     = "jessica"
  }
}

resource "aws_ssm_parameter" "jessica_port" {
  name        = "/jessica/${var.environment}/port"
  description = "Port configuration for Jessica service"
  type        = "String"
  value       = "9020"
  
  tags = {
    Environment = var.environment
    Service     = "jessica"
  }
}

resource "aws_ssm_parameter" "jessica_debug" {
  name        = "/jessica/${var.environment}/debug"
  description = "Debug flag for Jessica service"
  type        = "String"
  value       = "false"
  
  tags = {
    Environment = var.environment
    Service     = "jessica"
  }
}

# IAM Policy for SSM Parameter access
resource "aws_iam_policy" "jessica_ssm_access" {
  name        = "jessica-ssm-access-${var.environment}"
  description = "Allow access to Jessica SSM parameters"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "ssm:GetParameters",
          "secretsmanager:GetSecretValue",
          "kms:Decrypt"
        ]
        Resource = [
          "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/jessica/${var.environment}/*",
          aws_ssm_parameter.jessica_base_path.arn,
          aws_ssm_parameter.jessica_root_path.arn,
          aws_ssm_parameter.jessica_api_url.arn,
          aws_ssm_parameter.jessica_host.arn, 
          aws_ssm_parameter.jessica_port.arn,
          aws_ssm_parameter.jessica_debug.arn,
          aws_ssm_parameter.jessica_eleven_labs_api_key.arn,
          "arn:aws:kms:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:key/*"
        ]
      }
    ]
  })
}

# Include ECR module
module "ecr" {
  source = "./aws/ecr"
  
  repository_name = "jessica"
  image_tag_mutability = "MUTABLE"
}

# Include IAM module for GitHub Actions deployment
module "iam" {
  source = "./aws/iam"
  
  role_name = "jessica-github-actions-deployment-role"
  ecr_repository_arns = [module.ecr.repository_arn]
  github_oidc_provider_arn = "arn:aws:iam::927485958639:oidc-provider/token.actions.githubusercontent.com"
  github_org = "georgi-io"
  github_repo = "jessica"
  allowed_branches = ["main", "develop"]
}

# Add IAM policy for API Gateway integration
resource "aws_iam_role_policy" "api_gateway" {
  name = "api-gateway-integration-policy"
  role = module.iam.deployment_role_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "apigateway:GET",
          "apigateway:UPDATE",
          "apigateway:PUT"
        ]
        Resource = [
          "arn:aws:apigateway:${var.aws_region}::/apis/${data.terraform_remote_state.infrastructure.outputs.api_gateway_id}/*"
        ]
      }
    ]
  })
}

# Include ECS Fargate module
module "ecs" {
  source = "./aws/ecs"
  
  service_name = "jessica"
  container_image = "${module.ecr.repository_url}:latest"
  container_port = 9020
  
  cpu = 512
  memory = 1024
  
  # Pass VPC and subnet information from the infrastructure remote state
  vpc_id = data.terraform_remote_state.infrastructure.outputs.vpc_id
  private_subnet_ids = data.terraform_remote_state.infrastructure.outputs.private_subnet_ids
  
  # Pass ECS cluster information
  ecs_cluster_arn = data.terraform_remote_state.infrastructure.outputs.ecs_cluster_arn
  ecs_cluster_name = data.terraform_remote_state.infrastructure.outputs.ecs_cluster_name
  
  # Pass central ALB information
  central_alb_arn = data.terraform_remote_state.infrastructure.outputs.central_alb_arn
  central_alb_https_listener_arn = data.terraform_remote_state.infrastructure.outputs.central_alb_https_listener_arn
  
  # We're replacing environment variables with SSM parameters
  # These are now handled as secrets in the task definition
  secrets = {
    "BASE_PATH" = aws_ssm_parameter.jessica_base_path.arn,
    "ROOT_PATH" = aws_ssm_parameter.jessica_root_path.arn,
    "API_URL" = aws_ssm_parameter.jessica_api_url.arn,
    "HOST" = aws_ssm_parameter.jessica_host.arn,
    "PORT" = aws_ssm_parameter.jessica_port.arn,
    "DEBUG" = aws_ssm_parameter.jessica_debug.arn,
    "ELEVEN_LABS_API_KEY" = aws_ssm_parameter.jessica_eleven_labs_api_key.arn
  }
  
  # Attach the SSM access policy to the ECS task execution role
  additional_execution_role_policy_arns = [aws_iam_policy.jessica_ssm_access.arn]
  
  # Enable cost optimization through scheduled scaling
  enable_scheduled_scaling = true
  scale_up_cron = "cron(0 7 ? * MON-FRI *)"   # 7:00 AM UTC Monday-Friday
  scale_down_cron = "cron(0 19 ? * MON-FRI *)" # 7:00 PM UTC Monday-Friday
}

# Include API Gateway integration module
module "api_gateway" {
  source = "./aws/api_gateway"
  
  # Service information
  # Hinweis: Die Route "ANY /jessica-service/{proxy+}" existiert bereits im API Gateway
  # und wird durch das zentrale Infrastructure-Repository verwaltet.
  # Dieses Modul erstellt nur noch die Integration, aber nicht mehr die Route selbst.
  service_name = "jessica-service"
  container_port = 9020
  
  # TLS configuration
  tls_server_name = "api.run.georgi.io"
  
  # AWS profile
  aws_profile = var.aws_profile
  
  # Pass infrastructure outputs
  api_gateway_id = data.terraform_remote_state.infrastructure.outputs.api_gateway_id
  vpc_link_id = data.terraform_remote_state.infrastructure.outputs.vpc_link_id
  central_alb_https_listener_arn = data.terraform_remote_state.infrastructure.outputs.central_alb_https_listener_arn
} 