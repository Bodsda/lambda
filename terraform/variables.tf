variable "global_tags" {
  type        = map(any)
  description = " Global tags to be applied to all deployed objects"
}

# data supplied by the ./environments/*/<account>/*.tfvars files
variable "iics_instances" {
  type        = set(string)
  description = "List of IICS EC2 instances to be given cross-account s3 access "
}

variable "event_schedule_expression" {
  type        = string
  description = "EventBridge extended cron schedule"
  default     = "cron(0/5 9-19 ? * MON-FRI *)"
}

variable "event_schedule_description" {
  type        = string
  description = "Describes the intended cron schedule in the EventBridge trigger"
  default     = "'Checks all buckets for ipaas tags once every 5 minutes (weekdays 9.00am - 7.00pm UTC) in dev test mode'"
}
