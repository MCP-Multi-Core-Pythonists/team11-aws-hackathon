variable "api_id" {
  description = "API Gateway HTTP API ID"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# API Gateway HTTP API (to be imported)
resource "aws_apigatewayv2_api" "http" {
  name          = "sync-hub-api"
  protocol_type = "HTTP"
  description   = "Sync Hub HTTP API"

  cors_configuration {
    allow_credentials = true
    allow_headers     = ["authorization", "content-type", "x-amz-date", "x-amz-security-token", "x-amz-user-agent"]
    allow_methods     = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    allow_origins     = ["*"]
    expose_headers    = ["date", "keep-alive"]
    max_age          = 86400
  }

  tags = var.tags
}

# Default stage (may need to be imported separately)
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_rate_limit  = 1000
    throttling_burst_limit = 2000
  }

  tags = var.tags
}
