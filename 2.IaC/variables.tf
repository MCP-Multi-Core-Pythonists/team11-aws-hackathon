variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "account_id" {
  description = "AWS Account ID"
  type        = string
  default     = "851725240440"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "sync-hub"
}

# Existing resource identifiers
variable "existing_cloudfront_distribution_id" {
  description = "Existing CloudFront distribution ID"
  type        = string
  default     = "EPUT16LI6OAAI"
}

variable "existing_s3_bucket_name" {
  description = "Existing S3 bucket name"
  type        = string
  default     = "sync-hub-web-1757132517"
}

variable "existing_api_gateway_id" {
  description = "Existing API Gateway HTTP API ID"
  type        = string
  default     = "l7ycatge3j"
}

variable "existing_cognito_user_pool_id" {
  description = "Existing Cognito User Pool ID"
  type        = string
  default     = "us-east-1_ARkd0dYPj"
}

variable "existing_cognito_client_id" {
  description = "Existing Cognito App Client ID"
  type        = string
  default     = "7n568rmtbtp2tt8m0av2hl0f2n"
}

variable "existing_cognito_domain" {
  description = "Existing Cognito Hosted UI domain"
  type        = string
  default     = "sync-hub-851725240440"
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
