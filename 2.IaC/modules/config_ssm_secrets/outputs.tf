output "google_client_id" {
  description = "Google OAuth client ID from SSM"
  value       = data.aws_ssm_parameter.google_client_id.value
}

output "google_scopes" {
  description = "Google OAuth scopes from SSM"
  value       = data.aws_ssm_parameter.google_scopes.value
}

output "google_client_secret" {
  description = "Google OAuth client secret from Secrets Manager"
  value       = data.aws_secretsmanager_secret_version.google_client_secret.secret_string
  sensitive   = true
}

output "secret_arn" {
  description = "Secrets Manager secret ARN"
  value       = data.aws_secretsmanager_secret.google_client_secret.arn
}

output "ssm_parameter_names" {
  description = "List of SSM parameter names"
  value = [
    data.aws_ssm_parameter.google_client_id.name,
    data.aws_ssm_parameter.google_scopes.name
  ]
}
