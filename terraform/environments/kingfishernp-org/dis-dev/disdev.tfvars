global_tags = {
  Orchestration       = "TF"
  Technical_Owner     = "Cloud Solution Services"
  Environment         = "dev"
  Charge_Code         = "15445"
  OpCo                = "kits"
  Service             = "ipaas_cross_account_access"
  dt_servicenow_owner = "Cloud Solution Services"
}

# resource "aws_cloudwatch_event_rule" "DISDailyBucketTagChecker"
event_schedule_description = "Checks all buckets for ipaas tags run every 5 minutes during code testing"
event_schedule_expression  = "cron(0/5 9-19 ? * MON-FRI *)"

# list of EC2 instances
iics_instances = [
  "sstest6",
  "sstest-rhel7"
]
