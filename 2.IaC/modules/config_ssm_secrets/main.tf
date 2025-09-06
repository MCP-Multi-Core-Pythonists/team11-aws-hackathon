# Data sources for existing SSM parameters
data "aws_ssm_parameter" "google_client_id" {
  name = "/synchub/google/client_id"
}

data "aws_ssm_parameter" "google_scopes" {
  name = "/synchub/google/scopes"
}

# Data sources for existing Secrets Manager secret
data "aws_secretsmanager_secret" "google_client_secret" {
  name = "synchub/google/client_secret"
}

data "aws_secretsmanager_secret_version" "google_client_secret" {
  secret_id = data.aws_secretsmanager_secret.google_client_secret.id
}
