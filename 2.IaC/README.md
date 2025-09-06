# Sync Hub Terraform Infrastructure

This Terraform configuration manages the existing Sync Hub infrastructure in AWS us-east-1, adopting resources via `terraform import` without destructive changes.

## Architecture

The infrastructure consists of:
- **CloudFront Distribution** - Web console delivery
- **S3 Bucket** - Static web assets storage
- **Cognito User Pool** - Authentication and user management
- **API Gateway HTTP API** - Backend API endpoints
- **SSM Parameters & Secrets** - Configuration management

## Prerequisites

- Terraform 1.9+
- AWS CLI configured with appropriate permissions
- Python 3.7+ (for bootstrap script)

## Quick Start

### 1. Bootstrap Backend (One-time)

```bash
cd terraform
python3 bootstrap.py
```

This creates:
- S3 bucket: `sync-hub-tfstate-851725240440-us-east-1`
- DynamoDB table: `tfstate-locks`

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Import Existing Resources

```bash
# Import Cognito resources
terraform import module.identity_cognito.aws_cognito_user_pool.main us-east-1_ARkd0dYPj
terraform import module.identity_cognito.aws_cognito_user_pool_client.web us-east-1_ARkd0dYPj/7n568rmtbtp2tt8m0av2hl0f2n
terraform import module.identity_cognito.aws_cognito_user_pool_domain.domain us-east-1_ARkd0dYPj/sync-hub-851725240440

# Import CloudFront distribution
terraform import module.edge_cloudfront.aws_cloudfront_distribution.web EPUT16LI6OAAI

# Import S3 bucket
terraform import module.web_s3.aws_s3_bucket.web sync-hub-web-1757132517

# Import API Gateway
terraform import module.api_http.aws_apigatewayv2_api.http l7ycatge3j
```

### 4. Plan and Apply

```bash
terraform plan -var-file=envs/dev.tfvars
terraform apply -var-file=envs/dev.tfvars
```

## Automated Deployment

Use the deployment script for a guided workflow:

```bash
python3 deploy.py
```

## Module Structure

```
terraform/
├── main.tf              # Root module configuration
├── versions.tf          # Terraform and provider versions
├── providers.tf         # AWS provider configuration
├── backend.tf           # Remote state backend
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── import.tf            # Import documentation
├── bootstrap.py         # Backend bootstrap script
├── deploy.py            # Automated deployment script
├── modules/
│   ├── config_ssm_secrets/    # SSM parameters and secrets
│   ├── web_s3/               # S3 bucket for web assets
│   ├── edge_cloudfront/      # CloudFront distribution
│   ├── identity_cognito/     # Cognito user pool and client
│   ├── api_http/             # API Gateway HTTP API
│   └── observability/        # CloudWatch resources
└── envs/
    └── dev.tfvars            # Environment-specific variables
```

## Security Considerations

- All secrets are referenced via data sources, never hardcoded
- S3 bucket has public access blocked
- CloudFront uses Origin Access Control (OAC)
- Cognito client is configured as public client with PKCE
- State bucket has versioning and encryption enabled

## Outputs

After successful deployment, Terraform outputs:

- `api_base_url` - API Gateway endpoint
- `cloudfront_domain_name` - CloudFront distribution domain
- `s3_bucket_name` - Web assets bucket name
- `cognito_user_pool_id` - Cognito User Pool ID
- `cognito_client_id` - Cognito App Client ID
- `hosted_ui_domain` - Cognito Hosted UI domain
- `primary_endpoints` - Summary of all service endpoints

## Troubleshooting

### Import Failures

If imports fail, check:
1. Resource IDs are correct
2. AWS credentials have sufficient permissions
3. Resources exist in the specified region

### State Conflicts

If state conflicts occur:
1. Check for existing state in the backend
2. Use `terraform state list` to see imported resources
3. Use `terraform state rm` to remove incorrect imports

### Permission Issues

Required IAM permissions:
- S3: Full access to state bucket
- DynamoDB: Read/write access to lock table
- CloudFront: Read/write access to distributions
- Cognito: Read/write access to user pools
- API Gateway: Read/write access to APIs
- SSM: Read access to parameters
- Secrets Manager: Read access to secrets

## Maintenance

### Adding New Resources

1. Add resource definitions to appropriate modules
2. Update variables and outputs as needed
3. Import existing resources if they exist
4. Plan and apply changes

### Updating Existing Resources

1. Modify resource configurations
2. Run `terraform plan` to review changes
3. Apply changes with `terraform apply`

### State Management

- State is stored in S3 with DynamoDB locking
- State file is encrypted at rest
- Versioning is enabled for state recovery

## Support

For issues with this Terraform configuration:
1. Check the troubleshooting section above
2. Review Terraform and AWS provider documentation
3. Ensure all prerequisites are met
