#### DPS Account ####

resource "aws_iam_role" "dis_aws_bucket_role" {
  name = "dis-s3-bucket-cross-account-access"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Action    = "sts:AssumeRole",
        Principal = { "AWS" : "arn:aws:iam::${data.aws_caller_identity.dis.account_id}:root" }
    }]
  })
  tags = merge(var.global_tags, {
    git_commit           = "5762c4d57ce17178bcce6773069eaf80107d5019"
    git_file             = "terraform/main.tf"
    git_last_modified_at = "2022-06-13 09:17:35"
    git_last_modified_by = "steven.soutar@kingfisher.com"
    git_modifiers        = "steven.soutar"
    git_org              = "group_iaas"
    git_repo             = "customer-applications/ipaas_cross_account_iam_role"
    yor_name             = "dis_aws_bucket_role"
    yor_trace            = "99446362-a2c6-45ef-8f34-3c0eb4c43f47"
  })
  provider = aws.dps
}

#### DIS Account ####

resource "aws_iam_policy" "dis_aws_bucket_policy" {
  name        = "dis-s3-bucket-cross-account-access-policy"
  description = "allow assuming prod_s3 role"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "sts:AssumeRole",
        Resource = "arn:aws:iam::${data.aws_caller_identity.dps.account_id}:role/${aws_iam_role.dis_aws_bucket_role.name}"
    }]
  })
  tags = merge(var.global_tags, {
    git_commit           = "5762c4d57ce17178bcce6773069eaf80107d5019"
    git_file             = "terraform/main.tf"
    git_last_modified_at = "2022-06-13 09:17:35"
    git_last_modified_by = "steven.soutar@kingfisher.com"
    git_modifiers        = "steven.soutar"
    git_org              = "group_iaas"
    git_repo             = "customer-applications/ipaas_cross_account_iam_role"
    yor_name             = "dis_aws_bucket_policy"
    yor_trace            = "645a0f9c-d581-474c-83d2-9a2adecd89b1"
  })
  provider = aws.dis
}

resource "aws_iam_role_policy_attachment" "iics_buckets" {
  for_each   = var.iics_instances
  policy_arn = aws_iam_policy.dis_aws_bucket_policy.arn
  role       = each.value
  provider   = aws.dis
}
