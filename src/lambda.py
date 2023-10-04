import boto3
from botocore.exceptions import ClientError
import logging
import json
 sys getsizeof


def lambda_handler(event, context):
    s3 = boto3.resource("s3")
    buckets = s3.buckets.all()

    ipaas_read_buckets = []
    ipaas_write_buckets = []

    iam = boto3.client("iam")

    acc_id = boto3.client("sts").get_caller_identity().get("Account")

    role_name = "dis-s3-bucket-cross-account-access"
    resource = boto3.resource("iam")
    role = resource.Role(role_name)

    logger = logging.getLogger("dis-aws-cross-account-s3-access")
    logger.setLevel(logging.INFO)

    logger.info("Getting eligible s3 buckets for read")
    for bucket in buckets:
        try:
            tag_set = s3.BucketTagging(bucket.name).tag_set
            if any(
                tag["Key"] == "ipaas_transfer_enabled" and tag["Value"] == "read"
                for tag in tag_set
            ):
                ipaas_read_buckets.append(bucket.name)
        except ClientError as e:
            pass

    logger.info("Getting eligible s3 buckets for read/write")
    for bucket in buckets:
        try:
            tag_set = s3.BucketTagging(bucket.name).tag_set
            if any(
                tag["Key"] == "ipaas_transfer_enabled" and tag["Value"] == "write"
                for tag in tag_set
            ):
                ipaas_write_buckets.append(bucket.name)
        except ClientError as e:
            pass

    logger.info("Assigning policy for write buckets")
    if len(ipaas_write_buckets) > 0:
        resource_list_write = []
        resource_list_write_any = []
        for ipaas_bucket in ipaas_write_buckets:
            resource_list_write.append("arn:aws:s3:::" + ipaas_bucket)
            resource_list_write_any.append("arn:aws:s3:::" + ipaas_bucket + "/*")
        ipaas_write_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AccountBucketPermissions",
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutLifecycleConfiguration",
                        "s3:ListBucketMultipartUploads",
                        "s3:ListBucket",
                        "s3:GetLifecycleConfiguration",
                        "s3:GetBucketLocation",
                        "s3:PutLifecycleConfiguration",
                    ],
                    "Resource": resource_list_write,
                },
                {
                    "Sid": "AccountObjectPermissions",
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObjectAcl",
                        "s3:PutObject",
                        "s3:GetObjectVersionAcl",
                        "s3:GetObjectVersion",
                        "s3:GetObjectAcl",
                        "s3:GetObject",
                        "s3:DeleteObjectVersion",
                        "s3:DeleteObject",
                        "s3:AbortMultipartUpload",
                    ],
                    "Resource": resource_list_write_any,
                },
            ],
        }

        policy_arn = "arn:aws:iam::" + acc_id + ":policy/dis-managed-ipaas-write-policy"

        try:
            response = iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        except ClientError as e:
            pass

        try:
            response = iam.list_policy_versions(PolicyArn=policy_arn)
            for policy_version in response["Versions"]:
                if policy_version["IsDefaultVersion"]:
                    continue
                response = iam.delete_policy_version(
                    PolicyArn=policy_arn, VersionId=policy_version["VersionId"]
                )
            response = iam.delete_policy(PolicyArn=policy_arn)
        except ClientError as e:
            pass

        response = iam.create_policy(
            PolicyName="dis-managed-ipaas-write-policy",
            PolicyDocument=json.dumps(ipaas_write_policy),
            Description="Write bucket policy for ipaas managed by dis lambda",
            Tags=[
                {"Key": "Technical_Owner", "Value": "dis"},
                {"Key": "Charge_Code", "Value": "15445"},
            ],
        )

        role.attach_policy(PolicyArn=policy_arn)
        logger.info(policy_arn + " has been attached to the IAM role " + role_name)

    logger.info("Assigning policy for read buckets")
    if len(ipaas_read_buckets) > 0:
        resource_list_read = []
        resource_list_read_any = []
        for ipaas_bucket in ipaas_read_buckets:
            resource_list_read.append("arn:aws:s3:::" + ipaas_bucket)
            resource_list_read_any.append("arn:aws:s3:::" + ipaas_bucket + "/*")

        ipaas_read_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AccountBucketPermissions",
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucketMultipartUploads",
                        "s3:ListBucket",
                        "s3:GetBucketLocation",
                        "s3:GetLifecycleConfiguration",
                    ],
                    "Resource": resource_list_read,
                },
                {
                    "Sid": "AccountObjectPermissions",
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObjectVersionAcl",
                        "s3:GetObjectVersion",
                        "s3:GetObjectAcl",
                        "s3:GetObject",
                    ],
                    "Resource": resource_list_read_any,
                },
            ],
        }


        policy_arn = "arn:aws:iam::" + acc_id + ":policy/dis-managed-ipaas-read-policy"

        try:
            response = iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        except ClientError as e:
            pass

        try:
            response = iam.list_policy_versions(PolicyArn=policy_arn)
            for policy_version in response["Versions"]:
                if policy_version["IsDefaultVersion"]:
                    continue
                response = iam.delete_policy_version(
                    PolicyArn=policy_arn, VersionId=policy_version["VersionId"]
                )
            response = iam.delete_policy(PolicyArn=policy_arn)
        except ClientError as e:
            pass

        response = iam.create_policy(
            PolicyName="dis-managed-ipaas-read-policy",
            PolicyDocument=json.dumps(ipaas_read_policy),
            Description="Read bucket policy for ipaas managed by dis lambda",
            Tags=[
                {"Key": "Technical_Owner", "Value": "dis"},
                {"Key": "Charge_Code", "Value": "15445"},
            ],
        )

        role.attach_policy(PolicyArn=policy_arn)
        logger.info(policy_arn + " has been attached to the IAM role " + role_name)
