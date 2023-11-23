# tflint-ignore: terraform_naming_convention
output "S3_Storage_Account_AssumeRole_ARN" {
  value       = aws_iam_role.dis_aws_bucket_role.arn
  description = "The ARN of the S3 dis_aws_bucket_role"
}

output "current_time" {
  value = timestamp()
  description = "Current time"
}

