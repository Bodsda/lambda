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
event_schedule_description = "Checks all buckets for ipaas tags once every 12 hours (weekdays 9.00am - 7.00pm UTC) in Production mode"
event_schedule_expression  = "cron(0 0/12 ? * MON-FRI *)"

# EC2 instances - IAM Role names
iics_instances = [
  "int-iics-cp-sa-prod-1",
  "int-iics-cp-sa-prod-2"
]
