data "aws_caller_identity" "dis" {
  provider = aws.dis
}

data "aws_caller_identity" "dps" {
  provider = aws.dps
}
