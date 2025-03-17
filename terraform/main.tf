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

# Include ECS Fargate module
module "ecs" {
  source = "./aws/ecs"
  
  service_name = "jessica"
  container_image = "${module.ecr.repository_url}:latest"
  container_port = 9020
  mcp_port = 9022
  
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
  
  # Environment variables for the container
  environment_variables = {
    HOST = "0.0.0.0"
    PORT = "9020"
    MCP_PORT = "9022"
    DEBUG = "false"
  }
  
  # Enable cost optimization through scheduled scaling
  enable_scheduled_scaling = true
  scale_up_cron = "cron(0 7 ? * MON-FRI *)"   # 7:00 AM UTC Monday-Friday
  scale_down_cron = "cron(0 19 ? * MON-FRI *)" # 7:00 PM UTC Monday-Friday
}

# Include API Gateway integration module
module "api_gateway" {
  source = "./aws/api_gateway"
  
  # API Gateway routes
  api_gateway_route_key = "ANY /jessica/{proxy+}"
  mcp_gateway_route_key = "ANY /jessica/sse/{proxy+}"
  
  # Service information
  service_name = "jessica"
  container_port = 9020
  mcp_port = 9022
  
  # TLS configuration
  tls_server_name = "api.run.georgi.io"  # Kann später durch eine Variable ersetzt werden
  
  # Pass infrastructure outputs
  api_gateway_id = data.terraform_remote_state.infrastructure.outputs.api_gateway_id
  vpc_link_id = data.terraform_remote_state.infrastructure.outputs.vpc_link_id
  central_alb_https_listener_arn = data.terraform_remote_state.infrastructure.outputs.central_alb_https_listener_arn
} 