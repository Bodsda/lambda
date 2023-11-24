# terraform-init

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 4.8 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 4.67.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_dynamodb_table"></a> [dynamodb\_table](#module\_dynamodb\_table) | git::https://gitlab.kfplc.com/group_iaas/aws-terraform-modules.git//dynamodb_terraform_lock | v1.10.0 |
| <a name="module_s3_bucket"></a> [s3\_bucket](#module\_s3\_bucket) | git::https://gitlab.kfplc.com/group_iaas/aws-terraform-modules.git//s3_bucket | v1.5.1 |

## Resources

| Name | Type |
|------|------|
| [aws_s3_bucket_public_access_block.private_s3](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_force_destroy"></a> [force\_destroy](#input\_force\_destroy) | A boolean that indicates all objects (including any locked objects) should be deleted from the bucket so that the bucket can be destroyed without error. These objects are not recoverable. Defaults to 'false'. | `bool` | n/a | yes |
| <a name="input_global_tags"></a> [global\_tags](#input\_global\_tags) | A set of tags to apply to all 'taggable' resources. | `map(string)` | n/a | yes |
| <a name="input_versioning"></a> [versioning](#input\_versioning) | (bool) - A state of versioning. | `bool` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_dynamodb_locking_table"></a> [dynamodb\_locking\_table](#output\_dynamodb\_locking\_table) | Outputs DynamoDB table. |
| <a name="output_s3_state_bucket"></a> [s3\_state\_bucket](#output\_s3\_state\_bucket) | Outputs S3 bucket. |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
