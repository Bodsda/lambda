module "dynamodb_table" {
  source                       = "git::https://gitlab.kfplc.com/group_iaas/aws-terraform-modules.git//dynamodb_terraform_lock?ref=v1.10.0"
  terraform_lock-dynamodb_name = "${var.global_tags.Technical_Owner}-${var.global_tags.Environment}-tfstate-table"
  tags = merge(var.global_tags, {
    git_commit           = "2e68a9900a22676f88e25d732d9059a1d9d6e419"
    git_file             = "terraform-init/dynamodb.tf"
    git_last_modified_at = "2023-10-12 14:11:49"
    git_last_modified_by = "steven.soutar@kingfisher.com"
    git_modifiers        = "sandip.mukherjee/steven.soutar"
    git_org              = "group_iaas"
    git_repo             = "customer-applications/ipaas_cross_account_iam_role"
    yor_name             = "dynamodb_table"
    yor_trace            = "2dcd8292-ab13-423e-9697-82e3069625b9"
  })
}
