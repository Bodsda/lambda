# Create an S3 bucket for out state file(s).
module "s3_bucket" {
  source        = "git::https://gitlab.kfplc.com/group_iaas/aws-terraform-modules.git//s3_bucket?ref=v1.5.1"
  bucket_name   = "${var.global_tags.Technical_Owner}-${var.global_tags.Environment}-ipaas-s3access-tfstate-bucket"
  versioning    = var.versioning
  force_destroy = var.force_destroy
  tags = merge(var.global_tags, {
    git_commit           = "77e71703a51bd2f0dc54c35825360bb4b6f0e078"
    git_file             = "terraform-init/s3_bucket.tf"
    git_last_modified_at = "2022-06-07 08:46:59"
    git_last_modified_by = "sandip.mukherjee@kingfisher.com"
    git_modifiers        = "sandip.mukherjee"
    git_org              = "group_iaas"
    git_repo             = "customer-applications/ipaas_cross_account_iam_role"
    yor_name             = "s3_bucket"
    yor_trace            = "553a8f7a-0433-4387-b139-b1df4ab8a457"
  })
}

# Manages S3 bucket-level Public Access Block configuration.
resource "aws_s3_bucket_public_access_block" "private_s3" {
  bucket                  = module.s3_bucket.bucket_id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
