output "api_id" {
  description = "API Gateway HTTP API ID"
  value       = aws_apigatewayv2_api.http.id
}

output "api_endpoint" {
  description = "API Gateway HTTP API endpoint"
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "api_arn" {
  description = "API Gateway HTTP API ARN"
  value       = aws_apigatewayv2_api.http.arn
}

output "execution_arn" {
  description = "API Gateway HTTP API execution ARN"
  value       = aws_apigatewayv2_api.http.execution_arn
}
