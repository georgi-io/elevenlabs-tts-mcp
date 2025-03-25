variable "api_gateway_id" {
  description = "ID of the API Gateway from the infrastructure remote state"
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

variable "route_id" {
  description = "ID der zentral erstellten Route, die mit der Integration verbunden werden soll"
  type        = string
  default     = ""
}

variable "jessica_service_integration_id" {
  description = "ID der Jessica Service Integration aus dem Hub, die aktualisiert werden soll"
  type        = string
  default     = ""
} 