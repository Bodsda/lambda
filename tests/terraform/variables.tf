variable "bucket_count" {
  type        = number
  default     = 10
  description = "the number of test s3 buckets to be created"
}

variable "read_or_write" {
  type        = string
  default     = "write"
  description = "set the AWS ipaas_transfer_enabled tag to either 'read' or 'write'"
}
