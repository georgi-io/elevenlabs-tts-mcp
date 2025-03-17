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