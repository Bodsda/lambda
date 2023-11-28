# terraform

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 5.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_archive"></a> [archive](#provider\_archive) | 2.4.0 |
| <a name="provider_aws.dis"></a> [aws.dis](#provider\_aws.dis) | 5.26.0 |
| <a name="provider_aws.dps"></a> [aws.dps](#provider\_aws.dps) | 5.26.0 |
| <a name="provider_null"></a> [null](#provider\_null) | 3.2.2 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.DISDailyBucketTagChecker](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.RunCheckDaily](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_iam_policy.dis_aws_bucket_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_policy.lambda_iam_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.dis_aws_bucket_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.lambda_iam_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.iics_buckets](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.lambda_iam_policy_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_lambda_function.dis_ipaas_bucket_tag_checker](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_permission.allow_cloudwatch_to_call_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [null_resource.my_lambda_buildstep](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [archive_file.lambda_zip](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [aws_caller_identity.dis](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_caller_identity.dps](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_event_schedule_description"></a> [event\_schedule\_description](#input\_event\_schedule\_description) | Describes the intended cron schedule in the EventBridge trigger | `string` | `"'Checks all buckets for ipaas tags once every 5 minutes (weekdays 9.00am - 7.00pm UTC) in dev test mode'"` | no |
| <a name="input_event_schedule_expression"></a> [event\_schedule\_expression](#input\_event\_schedule\_expression) | EventBridge extended cron schedule | `string` | `"cron(0/5 9-19 ? * MON-FRI *)"` | no |
| <a name="input_global_tags"></a> [global\_tags](#input\_global\_tags) | Global tags to be applied to all deployed objects | `map(any)` | n/a | yes |
| <a name="input_iics_instances"></a> [iics\_instances](#input\_iics\_instances) | List of IICS EC2 instances to be given cross-account s3 access | `set(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_S3_Storage_Account_AssumeRole_ARN"></a> [S3\_Storage\_Account\_AssumeRole\_ARN](#output\_S3\_Storage\_Account\_AssumeRole\_ARN) | The ARN of the S3 dis\_aws\_bucket\_role |
| <a name="output_current_time"></a> [current\_time](#output\_current\_time) | Current time |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
