variable "service_name" {
  description = "Name of the service"
  type        = string
  default     = "jessica"
}

variable "container_image" {
  description = "Docker image to use for the container (ECR repository URL with tag)"
  type        = string
}

variable "container_port" {
  description = "Port the container exposes for the API"
  type        = number
  default     = 9020
}

variable "host_port" {
  description = "Port exposed on the host for the API"
  type        = number
  default     = 9020
}

variable "mcp_port" {
  description = "Port for the MCP (Model Context Protocol) server"
  type        = number
  default     = 9022
}

variable "cpu" {
  description = "CPU units for the task (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "memory" {
  description = "Memory for the task in MB"
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Desired count of tasks"
  type        = number
  default     = 1
}

variable "enable_scheduled_scaling" {
  description = "Whether to enable scheduled autoscaling"
  type        = bool
  default     = true
}

variable "scale_up_cron" {
  description = "Cron expression for scaling up the service"
  type        = string
  default     = "cron(0 8 * * ? *)"  # 8:00 AM UTC
}

variable "scale_down_cron" {
  description = "Cron expression for scaling down the service"
  type        = string
  default     = "cron(0 20 * * ? *)"  # 8:00 PM UTC
}

variable "api_gateway_route_key" {
  description = "API Gateway route key for this service"
  type        = string
  default     = "ANY /jessica-service/{proxy+}"
}

variable "environment_variables" {
  description = "Environment variables for the container"
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Secrets to pass to the container"
  type        = map(string)
  default     = {}
}

variable "log_retention_days" {
  description = "Number of days to retain logs"
  type        = number
  default     = 7
}

variable "vpc_id" {
  description = "VPC ID from the infrastructure remote state"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs from the infrastructure remote state"
  type        = list(string)
}

variable "ecs_cluster_arn" {
  description = "ARN of the ECS cluster from the infrastructure remote state"
  type        = string
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster from the infrastructure remote state"
  type        = string
}

variable "central_alb_arn" {
  description = "ARN of the central Application Load Balancer from the infrastructure remote state"
  type        = string
}

variable "central_alb_https_listener_arn" {
  description = "ARN of the HTTPS listener of the central ALB"
  type        = string
} 