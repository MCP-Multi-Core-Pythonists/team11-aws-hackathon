variable "user_pool_id" {
  description = "Cognito User Pool ID"
  type        = string
}

variable "client_id" {
  description = "Cognito App Client ID"
  type        = string
}

variable "domain_name" {
  description = "Cognito domain name"
  type        = string
}

variable "google_client_id" {
  description = "Google OAuth client ID"
  type        = string
}

variable "google_scopes" {
  description = "Google OAuth scopes"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Cognito User Pool (to be imported)
resource "aws_cognito_user_pool" "main" {
  name = "sync-hub-users"

  # Basic configuration
  alias_attributes         = ["email"]
  auto_verified_attributes = ["email"]

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = var.tags
}

# Cognito User Pool Client (to be imported)
resource "aws_cognito_user_pool_client" "web" {
  name         = "sync-hub-client"
  user_pool_id = aws_cognito_user_pool.main.id

  # OAuth configuration
  generate_secret                      = false  # Public client
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  
  # Supported identity providers
  supported_identity_providers = ["COGNITO", "Google"]

  # Callback and logout URLs
  callback_urls = [
    "http://localhost:3000/callback",
    "https://d1iz4bwpzq14da.cloudfront.net/callback"
  ]
  
  logout_urls = [
    "http://localhost:3000",
    "https://d1iz4bwpzq14da.cloudfront.net"
  ]

  # Token validity
  refresh_token_validity = 30
  
  # Prevent user existence errors
  prevent_user_existence_errors = "ENABLED"
}

# Cognito User Pool Domain (to be imported)
resource "aws_cognito_user_pool_domain" "domain" {
  domain       = var.domain_name
  user_pool_id = aws_cognito_user_pool.main.id
}

# Google Identity Provider (optional - may need to be imported separately)
resource "aws_cognito_identity_provider" "google" {
  user_pool_id  = aws_cognito_user_pool.main.id
  provider_name = "Google"
  provider_type = "Google"

  provider_details = {
    client_id                = var.google_client_id
    client_secret            = "placeholder" # Will be updated via console/API
    authorize_scopes         = var.google_scopes
    attributes_url           = "https://people.googleapis.com/v1/people/me?personFields="
    attributes_url_add_attributes = "true"
    authorize_url            = "https://accounts.google.com/o/oauth2/v2/auth"
    oidc_issuer              = "https://accounts.google.com"
    token_request_method     = "POST"
    token_url                = "https://www.googleapis.com/oauth2/v4/token"
  }

  attribute_mapping = {
    email       = "email"
    given_name  = "given_name"
    family_name = "family_name"
    username    = "sub"
  }
}
