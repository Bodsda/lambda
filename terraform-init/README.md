# IPaaS Cross Account s3 Access

This module helps in creating a cross account s3 bucket read write access between IPaaS instances hosted in DIS and s3 bucket hosted in DPS accounts
This module created a cross account IAM role in DPS with a trusted relationship with DIS one hosting IPaaS instances.
This also creates a lambda function which is invoked and checks for tag ```ipaas_transfer_enabled``` in each bucket and if set to ```read``` it enables read access from DIS IAM role for that bucket, if tag value is ```write``` it enabled read write access.

## pre-commit hooks included

This module now includes a **.pre-commit-config.yaml** file, which will launch a suite of quality checks when you attempt to run the **git commit** command



```bash
pre-commit run --all-files                                                                                                                                                                     ✘
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
black....................................................................Passed
flake8...................................................................Passed
Terraform fmt............................................................Passed
Terraform docs...........................................................Passed
Terraform validate with tflint...........................................Passed
Terraform validate.......................................................Passed
```
All the tests included in this config currently pass all these jobs - this is what a clean run looks like.

If your code changes result in messages from the formatters or linters, you should fix your code, or include "# ignore-*" comments in the file, for edge cases which cannot be easily fixed

```bash
# tflint-ignore: terraform_naming_convention
resource "aws_cloudwatch_event_target" "RunCheckDaily" {
  rule      = aws_cloudwatch_event_rule.DISDailyBucketTagChecker.name
  target_id = "lambda"
  arn       = aws_lambda_function.dis_ipaas_bucket_tag_checker.arn
  provider  = aws.dps
}
```

If all else fails, you can include a **--no-verify** switch on the **commit** command (not recommended, but may be needed in some cases)

## Terraform workspaces

We use *Terraform Workspaces* to separate state files for different environments. The initial Terraform code located
in the `terraform-init` directory creates an S3 bucket for a state file and a DynamoDB table for locking purposes.
The code needs to be executed locally for a number of different environments existing in different AWS accounts,
hence the need to separate state files.

There are 4 workspaces:

- `default`
- `dis-dev`
- `dis-npd`
- `dis-prod`

Please note, that the `default` workspace is NOT in use.

## Backend configuration

Before running Terraform, you need to authenticate against the correct pair of AWS accounts.

### Example
for testing in dis-dev, using a dummy account to represent the DPS account, where the tagged buckets will sit

To deploy, go to the `terraform-init` folder and select the `dis-dev` workspace:

```terraform workspace select dis-dev```

### Setting up a new terraform workspace
To create an S3 backend configuration, with S3 storage and DynamoDB locking, run these commands in the `terraform-init` folder.

If the workspace & s3 backend already exist, you can skip this step

```bash
terraform init

terraform plan --var-file=./environments/kingfishernp-org/dis-dev/disdev.tfvars

terraform apply --var-file=./environments/kingfishernp-org/dis-dev/disdev.tfvars
```

List the available workspaces, and select the one you need

```bash
terraform workspace list
  default
* dis-dev
  dis-npd
  dis-prod

terraform workspace select dis-dev
```


## AWS Profiles

**First unset any AWS environment variable set.**

Please configure the source account hosting the IPaaS instances as ```dis``` and the s3 bucket account as ```dps``` in your AWS profile

```bash
export AWS_PROFILE=dis
aws configure sso
```
```bash
export AWS_PROFILE=dps
aws configure sso
```

**We have below setup**

| Tier  | dis               | dps  |
| ------------ |-------------------| ------------ |
| Sandpit  | dis-dev (IAD)     | KFPLC-DUMMY-SES-NP  |
|  Non Prod | dis-nonprod (IAN) | DPS non prod (AN)  |
|  Prod | dis-prod (IAP)    | DPS prod (AP)  |   |

## Dis-Dev

```bash
cd terraform

terraform init --backend-config=./environments/kingfishernp-org/dis-dev/disdev.backend

terraform plan --var-file=./environments/kingfishernp-org/dis-dev/disdev.tfvars

terraform apply --var-file=./environments/kingfishernp-org/dis-dev/disdev.tfvars
```

## Dis-Npd

```bash
cd terraform

terraform init --backend-config=./environments/kingfisherprod-org/dis-npd/disnpd.backend

terraform plan --var-file=./environments/kingfisherprod-org/dis-npd/disnpd.tfvars

terraform apply --var-file=./environments/kingfisherprod-org/dis-npd/disnpd.tfvars
```

## Dis-Prod

```bash
cd terraform

terraform init --backend-config=./environments/kingfisherprod-org/dis-prod/disprod.backend

terraform plan --var-file=./environments/kingfisherprod-org/dis-prod/disprod.tfvars

terraform apply --var-file=./environments/kingfisherprod-org/dis-prod/disprod.tfvars
```
