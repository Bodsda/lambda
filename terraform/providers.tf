terraform {
  required_version = "~> 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    region  = "eu-west-1"
    profile = "dis"
    # Key, bucket and dynamodb table names are provided by the backend.conf file.
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
