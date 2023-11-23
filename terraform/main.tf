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
}

resource "aws_iam_role_policy_attachment" "iics_buckets" {
  for_each   = var.iics_instances
  policy_arn = aws_iam_policy.dis_aws_bucket_policy.arn
  role       = each.value
  provider   = aws.dis
}
