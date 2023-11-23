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
  provider = aws.dps
  tags = {
    git_commit           = "6dad2010382f0d082b3b9599a3ff02ea251c0089"
    git_file             = "terraform/main.tf"
    git_last_modified_at = "2023-11-23 12:15:43"
    git_last_modified_by = "steven.soutar@kingfisher.com"
    git_modifiers        = "steven.soutar"
    git_org              = "Bodsda"
    git_repo             = "lambda"
    yor_name             = "dis_aws_bucket_role"
    yor_trace            = "72e75b8c-b596-4b3f-8c74-4905afd4de73"
  }
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
  provider = aws.dis
  tags = {
    git_commit           = "6dad2010382f0d082b3b9599a3ff02ea251c0089"
    git_file             = "terraform/main.tf"
    git_last_modified_at = "2023-11-23 12:15:43"
    git_last_modified_by = "steven.soutar@kingfisher.com"
    git_modifiers        = "steven.soutar"
    git_org              = "Bodsda"
    git_repo             = "lambda"
    yor_name             = "dis_aws_bucket_policy"
    yor_trace            = "b0e9c145-4e95-480b-be24-a1b7caad5681"
  }
}

resource "aws_iam_role_policy_attachment" "iics_buckets" {
  for_each   = var.iics_instances
  policy_arn = aws_iam_policy.dis_aws_bucket_policy.arn
  role       = each.value
  provider   = aws.dis
}
