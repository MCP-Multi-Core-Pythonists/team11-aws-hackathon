aws_region  = "us-east-1"
environment = "dev"
account_id  = "851725240440"

project_name = "sync-hub"

# Existing resource identifiers
existing_cloudfront_distribution_id = "EPUT16LI6OAAI"
existing_s3_bucket_name             = "sync-hub-web-1757132517"
existing_api_gateway_id             = "l7ycatge3j"
existing_cognito_user_pool_id       = "us-east-1_ARkd0dYPj"
existing_cognito_client_id          = "7n568rmtbtp2tt8m0av2hl0f2n"
existing_cognito_domain             = "sync-hub-851725240440"

common_tags = {
  project     = "sync-hub"
  environment = "dev"
  owner       = "platform-team"
}
