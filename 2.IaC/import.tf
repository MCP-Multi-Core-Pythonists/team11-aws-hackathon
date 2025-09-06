# Import commands for existing resources
# Run these commands after terraform init and before terraform plan

# Import Cognito User Pool
# terraform import module.identity_cognito.aws_cognito_user_pool.main us-east-1_ARkd0dYPj

# Import Cognito User Pool Client
# terraform import module.identity_cognito.aws_cognito_user_pool_client.web us-east-1_ARkd0dYPj/7n568rmtbtp2tt8m0av2hl0f2n

# Import Cognito User Pool Domain
# terraform import module.identity_cognito.aws_cognito_user_pool_domain.domain us-east-1_ARkd0dYPj/sync-hub-851725240440

# Import CloudFront Distribution
# terraform import module.edge_cloudfront.aws_cloudfront_distribution.web EPUT16LI6OAAI

# Import S3 Bucket
# terraform import module.web_s3.aws_s3_bucket.web sync-hub-web-1757132517

# Import API Gateway HTTP API
# terraform import module.api_http.aws_apigatewayv2_api.http l7ycatge3j

# Optional: Import S3 bucket policy if it exists
# terraform import module.web_s3.aws_s3_bucket_policy.web sync-hub-web-1757132517

# Note: Some resources may require additional imports for associated resources
# Check terraform plan output for any missing resources that need to be imported
