region        = "eu-west-1"
force_destroy = false
versioning    = true

global_tags = {
  Orchestration   = "TF"
  Technical_Owner = "dis"
  Environment     = "dis-dev"
  Charge_Code     = "15445"
  OpCo            = "kits"
  Service         = "ipaas_s3_cross_account"
  GitRepo         = "https://gitlab.kfplc.com/group_iaas/customer-applications/ipaas_cross_account_iam_role"
}
