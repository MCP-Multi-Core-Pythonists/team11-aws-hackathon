terraform {
  backend "s3" {
    bucket         = "sync-hub-tfstate-851725240440-us-east-1"
    key            = "sync-hub/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-locks"
    encrypt        = true
  }
}
