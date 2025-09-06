#!/usr/bin/env python3
"""
Terraform deployment script for Sync Hub infrastructure
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Success")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print("❌ Failed")
        if result.stderr:
            print(result.stderr)
        return False

def main():
    """Main deployment workflow"""
    print("🚀 Sync Hub Terraform Deployment")
    print("=" * 50)
    
    # Change to terraform directory
    if not os.path.exists('terraform'):
        print("❌ terraform directory not found. Run from project root.")
        sys.exit(1)
    
    os.chdir('terraform')
    
    # Step 1: Bootstrap backend (if needed)
    print("\n1️⃣ Checking backend resources...")
    if not run_command("python3 bootstrap.py", "Creating backend resources"):
        print("❌ Backend bootstrap failed")
        sys.exit(1)
    
    # Step 2: Initialize Terraform
    if not run_command("terraform init", "Initializing Terraform"):
        print("❌ Terraform init failed")
        sys.exit(1)
    
    # Step 3: Validate configuration
    if not run_command("terraform validate", "Validating Terraform configuration"):
        print("❌ Terraform validation failed")
        sys.exit(1)
    
    # Step 4: Plan (before imports)
    print("\n4️⃣ Running initial plan (expect many resources to be created)...")
    run_command("terraform plan -var-file=envs/dev.tfvars", "Initial Terraform plan")
    
    # Step 5: Import existing resources
    print("\n5️⃣ Importing existing resources...")
    
    import_commands = [
        ("module.identity_cognito.aws_cognito_user_pool.main", "us-east-1_ARkd0dYPj"),
        ("module.identity_cognito.aws_cognito_user_pool_client.web", "us-east-1_ARkd0dYPj/7n568rmtbtp2tt8m0av2hl0f2n"),
        ("module.identity_cognito.aws_cognito_user_pool_domain.domain", "us-east-1_ARkd0dYPj/sync-hub-851725240440"),
        ("module.edge_cloudfront.aws_cloudfront_distribution.web", "EPUT16LI6OAAI"),
        ("module.web_s3.aws_s3_bucket.web", "sync-hub-web-1757132517"),
        ("module.api_http.aws_apigatewayv2_api.http", "l7ycatge3j"),
    ]
    
    for resource_address, resource_id in import_commands:
        cmd = f"terraform import {resource_address} {resource_id}"
        if not run_command(cmd, f"Importing {resource_address}"):
            print(f"⚠️ Import failed for {resource_address} - may already be imported or not exist")
    
    # Step 6: Plan after imports
    print("\n6️⃣ Running plan after imports...")
    if not run_command("terraform plan -var-file=envs/dev.tfvars", "Post-import Terraform plan"):
        print("❌ Post-import plan failed")
        sys.exit(1)
    
    # Step 7: Ask for confirmation before apply
    print("\n7️⃣ Ready to apply changes...")
    response = input("Do you want to apply the changes? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        if run_command("terraform apply -var-file=envs/dev.tfvars -auto-approve", "Applying Terraform changes"):
            print("\n🎉 Deployment completed successfully!")
            
            # Show outputs
            print("\n📋 Terraform Outputs:")
            run_command("terraform output", "Displaying outputs")
        else:
            print("❌ Terraform apply failed")
            sys.exit(1)
    else:
        print("⏹️ Deployment cancelled by user")
    
    print("\n✅ Terraform deployment workflow completed!")

if __name__ == "__main__":
    main()
