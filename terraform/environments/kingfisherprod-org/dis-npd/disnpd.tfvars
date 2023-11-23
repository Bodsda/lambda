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
event_schedule_description = "Checks all buckets for ipaas tags once every 3 hours (weekdays only)"
event_schedule_expression  = "cron(0 0/3 ? * MON-FRI *)"
#event_schedule_description = "Checks all buckets for ipaas tags Non-production test schedule - weekdays on the hour, every hour"
#event_schedule_expression  = "cron(0 0/1 ? * MON-FRI *)"

# EC2 instances - IAM Role names
iics_instances = [
  "int-iics-cp-sa-dev-1",
  "int-iics-cp-sa-dev-2",
  "int-iics-cp-sa-qa-1",
  "int-iics-cp-sa-qa-2",
  "int-iics-cp-sa-perf-1",
  "int-iics-cp-sa-perf-2",
  "int-iics-cp-sa-uat-1",
  "int-iics-cp-sa-uat-2"
]
