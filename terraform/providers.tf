terraform {
  required_version = "~> 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "eu-west-1"
  profile = "dps"
  alias   = "dps"
}

provider "aws" {
  region  = "eu-west-1"
  profile = "dis"
  alias   = "dis"
}
