output "api_base_url" {
  description = "API Gateway base URL"
  value       = module.api_http.api_endpoint
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = module.edge_cloudfront.domain_name
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.web_s3.bucket_name
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = module.identity_cognito.user_pool_id
}

output "cognito_client_id" {
  description = "Cognito App Client ID"
  value       = module.identity_cognito.client_id
}

output "hosted_ui_domain" {
  description = "Cognito Hosted UI domain"
  value       = module.identity_cognito.hosted_ui_domain
}

output "ssm_param_names" {
  description = "SSM parameter names"
  value       = module.config_ssm_secrets.ssm_parameter_names
}

output "secret_arn" {
  description = "Secrets Manager secret ARN (value masked)"
  value       = module.config_ssm_secrets.secret_arn
  sensitive   = true
}

# Primary endpoints summary
output "primary_endpoints" {
  description = "Primary service endpoints"
  value = {
    api_base_url    = module.api_http.api_endpoint
    cloudfront_url  = "https://${module.edge_cloudfront.domain_name}/"
    hosted_ui_url   = "https://${module.identity_cognito.hosted_ui_domain}.auth.${var.aws_region}.amazoncognito.com"
  }
}
