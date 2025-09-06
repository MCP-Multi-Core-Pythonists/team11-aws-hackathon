output "log_groups" {
  description = "CloudWatch log groups"
  value       = data.aws_cloudwatch_log_groups.sync_hub.log_group_names
}

# output "dashboard_url" {
#   description = "CloudWatch dashboard URL"
#   value       = "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
# }
