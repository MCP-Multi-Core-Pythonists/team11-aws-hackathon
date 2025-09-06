# Data sources for existing configuration
module "config_ssm_secrets" {
  source = "./modules/config_ssm_secrets"
}

# Web S3 bucket module
module "web_s3" {
  source = "./modules/web_s3"
  
  bucket_name = var.existing_s3_bucket_name
  
  tags = var.common_tags
}

# CloudFront distribution module
module "edge_cloudfront" {
  source = "./modules/edge_cloudfront"
  
  distribution_id = var.existing_cloudfront_distribution_id
  s3_bucket_name  = var.existing_s3_bucket_name
  
  tags = var.common_tags
}

# Cognito identity module
module "identity_cognito" {
  source = "./modules/identity_cognito"
  
  user_pool_id    = var.existing_cognito_user_pool_id
  client_id       = var.existing_cognito_client_id
  domain_name     = var.existing_cognito_domain
  
  google_client_id = module.config_ssm_secrets.google_client_id
  google_scopes    = module.config_ssm_secrets.google_scopes
  
  tags = var.common_tags
}

# API Gateway HTTP API module
module "api_http" {
  source = "./modules/api_http"
  
  api_id = var.existing_api_gateway_id
  
  tags = var.common_tags
}

# Observability module (read-only data sources)
module "observability" {
  source = "./modules/observability"
  
  project_name = var.project_name
  environment  = var.environment
  
  tags = var.common_tags
}
