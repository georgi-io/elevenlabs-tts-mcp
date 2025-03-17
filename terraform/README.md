# Jessica Service Terraform Configuration

This directory contains the Terraform configuration for the Jessica service infrastructure. It follows the hub-and-spoke architecture described in the central georgi.io infrastructure repository.

## Components

- **ECR Repository**: For storing Docker images
- **VPC Integration**: Integration with the central VPC infrastructure
- **API Gateway Integration**: Integration with the central API Gateway (planned)

## Getting Started

### Prerequisites

- Terraform >= 1.0.0
- AWS CLI with SSO configuration
- yawsso (`pip install yawsso`) for AWS SSO credential management
- Appropriate AWS permissions

### AWS SSO Setup

1. Configure AWS SSO:
```bash
aws configure sso --profile georgi-io
# SSO Start URL: https://georgi-sso.awsapps.com/start
# SSO Region: eu-central-1
```

2. Login and sync credentials:
```bash
aws sso login --profile georgi-io
yawsso -p georgi-io  # Syncs SSO credentials with AWS CLI format
```

3. Verify setup:
```bash
aws sts get-caller-identity --profile georgi-io
```

### Terraform Commands

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy resources (use with caution)
terraform destroy
```

## Directory Structure

```
terraform/
├── main.tf                # Main Terraform configuration
├── variables.tf           # Variable definitions
├── outputs.tf             # Output definitions
├── terraform.tfvars       # Variable values
└── aws/                   # AWS-specific modules
    └── ecr/               # ECR repository module
        ├── main.tf        # ECR resource definitions
        ├── variables.tf   # ECR module variables
        └── outputs.tf     # ECR module outputs
```

## Remote State

This configuration uses the central S3 bucket for storing Terraform state:

```hcl
backend "s3" {
  bucket = "georgi-io-terraform-state"
  key    = "services/jessica/terraform.tfstate"
  region = "eu-central-1"
}
```

## Central Infrastructure Integration

This configuration integrates with the central infrastructure using Terraform remote state:

```hcl
data "terraform_remote_state" "infrastructure" {
  backend = "s3"
  config = {
    bucket = "georgi-io-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "eu-central-1"
  }
}
``` 