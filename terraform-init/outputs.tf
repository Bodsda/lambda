output "dynamodb_locking_table" {
  description = "Outputs DynamoDB table."
  value       = module.dynamodb_table
}

output "s3_state_bucket" {
  description = "Outputs S3 bucket."
  value       = module.s3_bucket
}
