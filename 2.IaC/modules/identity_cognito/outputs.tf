output "user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_arn" {
  description = "Cognito User Pool ARN"
  value       = aws_cognito_user_pool.main.arn
}

output "client_id" {
  description = "Cognito App Client ID"
  value       = aws_cognito_user_pool_client.web.id
}

output "hosted_ui_domain" {
  description = "Cognito Hosted UI domain"
  value       = aws_cognito_user_pool_domain.domain.domain
}

output "google_identity_provider_name" {
  description = "Google identity provider name"
  value       = aws_cognito_identity_provider.google.provider_name
}
