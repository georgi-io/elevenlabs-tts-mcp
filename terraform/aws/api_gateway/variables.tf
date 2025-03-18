variable "api_gateway_id" {
  description = "ID of the API Gateway from the infrastructure remote state"
  type        = string
}

variable "route_id" {
  description = "ID of the existing API Gateway route that needs to be updated"
  type        = string
}

variable "vpc_link_id" {
  description = "ID of the VPC Link from the infrastructure remote state"
  type        = string
}

variable "aws_profile" {
  description = "AWS Profile to use for AWS CLI commands"
  type        = string
  default     = "georgi-io"
}

variable "central_alb_https_listener_arn" {
  description = "ARN of the HTTPS listener of the central ALB"
  type        = string
}

variable "service_name" {
  description = "Name of the service"
  type        = string
}

variable "container_port" {
  description = "Port the container exposes for the API"
  type        = number
}

variable "tls_server_name" {
  description = "Server name to verify in the TLS handshake"
  type        = string
  default     = "api.run.georgi.io"
} 