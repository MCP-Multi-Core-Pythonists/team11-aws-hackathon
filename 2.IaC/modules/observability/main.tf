variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Data sources for existing CloudWatch resources (read-only)
data "aws_cloudwatch_log_groups" "sync_hub" {
  log_group_name_prefix = "/aws/lambda/sync-hub"
}

# Placeholder for CloudWatch dashboard (if exists)
# This would need to be imported if it exists
# resource "aws_cloudwatch_dashboard" "main" {
#   dashboard_name = "${var.project_name}-${var.environment}"
#   
#   dashboard_body = jsonencode({
#     widgets = [
#       {
#         type   = "metric"
#         x      = 0
#         y      = 0
#         width  = 12
#         height = 6
#         properties = {
#           metrics = [
#             ["AWS/ApiGateway", "Count", "ApiName", "sync-hub-api"],
#             [".", "Latency", ".", "."],
#             [".", "4XXError", ".", "."],
#             [".", "5XXError", ".", "."]
#           ]
#           period = 300
#           stat   = "Sum"
#           region = "us-east-1"
#           title  = "API Gateway Metrics"
#         }
#       }
#     ]
#   })
# }

# TODO: Add data sources for existing CloudWatch alarms if they exist
