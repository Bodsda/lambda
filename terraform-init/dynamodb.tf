module "dynamodb_table" {
  source                       = "git::https://gitlab.kfplc.com/group_iaas/aws-terraform-modules.git//dynamodb_terraform_lock?ref=v1.10.0"
  terraform_lock-dynamodb_name = "${var.global_tags.Technical_Owner}-${var.global_tags.Environment}-tfstate-table"
  tags = merge(var.global_tags, {
    git_commit           = "656b8abaa920e69b254aa1335fbe1513aba5c51c"
    git_file             = "terraform-init/dynamodb.tf"
    git_last_modified_at = "2023-11-23 13:56:46"
    git_last_modified_by = "steven.soutar@kingfisher.com"
    git_modifiers        = "steven.soutar"
    git_org              = "Bodsda"
    git_repo             = "lambda"
    yor_name             = "dynamodb_table"
    yor_trace            = "2dcd8292-ab13-423e-9697-82e3069625b9"
  })
}
