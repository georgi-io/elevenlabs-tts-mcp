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