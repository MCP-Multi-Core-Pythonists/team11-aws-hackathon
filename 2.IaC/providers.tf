provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      app        = "sync-hub"
      env        = var.environment
      managed_by = "terraform"
    }
  }
}
