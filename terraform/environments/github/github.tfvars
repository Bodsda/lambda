# resource "aws_cloudwatch_event_rule" "DISDailyBucketTagChecker"
event_schedule_description = "Checks all buckets for ipaas tags run every 5 minutes during code testing"
event_schedule_expression  = "cron(0/5 9-19 ? * MON-FRI *)"

# list of EC2 instances
iics_instances = [
  "webapp-example"
]
