variable "repository_name" {
  description = "Name of the ECR repository"
  type        = string
}

variable "image_tag_mutability" {
  description = "The tag mutability setting for the repository (MUTABLE or IMMUTABLE)"
  type        = string
  default     = "MUTABLE"
}

variable "scan_on_push" {
  description = "Indicates whether images are scanned after being pushed to the repository"
  type        = bool
  default     = true
}

variable "encryption_type" {
  description = "The encryption type to use for the repository (AES256 or KMS)"
  type        = string
  default     = "AES256"
}

variable "enable_lifecycle_policy" {
  description = "Whether to enable a lifecycle policy for automatic image cleanup"
  type        = bool
  default     = true
}

variable "image_count_to_keep" {
  description = "Number of images to keep when using lifecycle policy"
  type        = number
  default     = 10
} 