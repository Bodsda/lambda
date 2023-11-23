# tflint-ignore: terraform_required_providers
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda/src"
  output_path = "${path.module}/lambda.zip"
  depends_on  = [null_resource.my_lambda_buildstep]
  excludes    = ["__pycache__", "package", "venv"]
}

resource "aws_iam_role" "lambda_iam_role" {
  name = "dis_lambda_ipaas_bucket_checker_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

  provider = aws.dps
}

resource "aws_iam_policy" "lambda_iam_policy" {
  name        = "dis_lambda_policy"
  description = "policy for cross account s3 buckets check"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:GetBucketTagging",
        "s3:ListAllMyBuckets",
        "s3:ListBucket"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::*"
    },
    {
      "Action": [
        "iam:AttachRolePolicy",
        "iam:AttachUserPolicy",
        "iam:CreatePolicy",
        "iam:CreatePolicyVersion",
        "iam:TagPolicy",
        "iam:DeletePolicy",
        "iam:DeletePolicyVersion",
        "iam:DeleteRolePolicy",
        "iam:DeleteUserPolicy",
        "iam:DetachRolePolicy",
        "iam:DetachUserPolicy",
        "iam:ListUserPolicies",
        "iam:ListPolicyVersions",
        "iam:PutRolePolicy",
        "iam:PutUserPolicy",
        "iam:UpdateRole",
        "iam:ListAttachedRolePolicies"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:iam::*"
    },
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF

  provider = aws.dps
}

resource "aws_lambda_function" "dis_ipaas_bucket_tag_checker" {
  function_name = "dis-ipaas-cross-account-function"
  description   = "Check buckets for ipaas tag"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  role             = aws_iam_role.lambda_iam_role.arn

  #  Latest python interpreter available for AWS Lambda is current v3.11 (as at Oct 2023)
  runtime = "python3.11"
  timeout = 900
  handler = "lambda.lambda_handler"
  tags = merge(
    tomap({ "Name" = "dis-ipaas-cross-account-function" }),
    var.global_tags
    , {
      git_commit           = "ca139117092842200ad08362341999d7f3ed5f00"
      git_file             = "terraform/lambda.tf"
      git_last_modified_at = "2023-10-19 15:47:55"
      git_last_modified_by = "steven.soutar@kingfisher.com"
      git_modifiers        = "sandip.mukherjee/steven.soutar"
      git_org              = "group_iaas"
      git_repo             = "customer-applications/ipaas_cross_account_iam_role"
      yor_name             = "dis_ipaas_bucket_tag_checker"
      yor_trace            = "beeed9f1-8ded-4006-9471-dde40cc28bc1"
  })
  provider = aws.dps
}


resource "aws_iam_role_policy_attachment" "lambda_iam_policy_attachment" {
  role       = aws_iam_role.lambda_iam_role.name
  policy_arn = aws_iam_policy.lambda_iam_policy.arn
  provider   = aws.dps
}

# tflint-ignore: terraform_required_providers
resource "null_resource" "my_lambda_buildstep" {
  triggers = {
    handler      = base64sha256(file("../lambda/src/lambda.py"))
    requirements = base64sha256(file("../lambda/src/requirements.txt"))
    build        = base64sha256(file("../lambda/src/build.sh"))
  }

  provisioner "local-exec" {
    command = "../lambda/src/build.sh"
  }
}

# tflint-ignore: terraform_naming_convention
resource "aws_cloudwatch_event_rule" "DISDailyBucketTagChecker" {
  name        = "DIS-IpaaS-Bucket-Tag-Check"
  description = var.event_schedule_description
  /*     AWS Eventbridge extended cron format - for reference, \
         see https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cron-expressions.html */
  schedule_expression = var.event_schedule_expression

  tags = merge(var.global_tags, {
    git_commit           = "ef92b869f3cb63a7cc0be4d005235e1c4027198c"
    git_file             = "terraform/lambda.tf"
    git_last_modified_at = "2023-11-02 12:10:42"
    git_last_modified_by = "steven.soutar@kingfisher.com"
    git_modifiers        = "sandip.mukherjee/steven.soutar"
    git_org              = "group_iaas"
    git_repo             = "customer-applications/ipaas_cross_account_iam_role"
    yor_name             = "DISDailyBucketTagChecker"
    yor_trace            = "079211dc-a52f-4860-adf7-c6aa5ea5c157"
  })
  provider = aws.dps
}

# tflint-ignore: terraform_naming_convention
resource "aws_cloudwatch_event_target" "RunCheckDaily" {
  rule      = aws_cloudwatch_event_rule.DISDailyBucketTagChecker.name
  target_id = "lambda"
  arn       = aws_lambda_function.dis_ipaas_bucket_tag_checker.arn
  provider  = aws.dps
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dis_ipaas_bucket_tag_checker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.DISDailyBucketTagChecker.arn
  provider      = aws.dps
}
