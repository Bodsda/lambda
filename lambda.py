"""Module to detach, delete and re-create permission policies for s3 bucket and s3 bucket object access"""

from sys import getsizeof
from itertools import zip_longest
import logging
import json

import boto3
from botocore.exceptions import ClientError

s3 = boto3.resource("s3")
buckets = s3.buckets.all()

iam = boto3.client("iam")

logger = logging.getLogger("dis-aws-cross-account-s3-access")
logger.setLevel(logging.INFO)

def get_buckets(s3buckets, rw_tag):
    """get_buckets takes a list of s3 buckets and a rw_tag("read", "write") as parameters, and returns all buckets with that tag that is also marked "ipaas_transfer_enabled"."""
    ipaas_buckets = []

    for bucket in s3buckets:
        try:
            tag_set = s3.BucketTagging(bucket.name).tag_set
        except ClientError as error_client:
            logger.error("ClientError from botocore.exceptions raised when attempting s3.BucketTagging().tag_set")
            logger.error("Error: %s", error_client)
            continue
        except Exception as error_exception:
            logger.error("General Exception caught")
            logger.error("Error: %s", error_exception)
            continue

        for item in tag_set:
            if item["Key"] == "ipaas_transfer_enabled" and item["Value"] == rw_tag:
                ipaas_buckets.append(bucket.name)

    return ipaas_buckets

def get_role_policies(role_name, role_prefix):
    """get_role_polciies accepts a role name and a role prefix, then returns a list of dictionary objects that contain that policy filtered by prefix"""

    filtered_policies = []
    response=""
    try:
        response = iam.list_attached_role_policies(RoleName=role_name)
        for policy in response["AttachedPolicies"]:
            if role_prefix in policy["PolicyArn"]:
                filtered_policies.append({policy["PolicyName"]:policy["PolicyArn"]})
    except Exception as error_exception:
        logger.error("General Exception caught")
        logger.error("Error: %s", error_exception)

    return filtered_policies


def generate_resource_list(s3buckets, objects=False):
    """generate_resource_list takes a list of s3 buckets and optionally a parameter to indicate if you want the resource list to return objects instead of buckets."""
    resource_list = []

    for item in s3buckets:
        if not objects:
            resource_list.append("arn:aws:s3:::" + item)
        else:
            resource_list.append("arn:aws:s3:::" + item + "/*")

    return resource_list

def generate_policy(s3buckets, objects=False):
    """generate_policy takes a list of s3 buckets and optionally a parameter to indicate if you want the resultant policy data to be for buckets or objects."""
    # ipaas_policy template is 343 bytes when the dict is represented as a string
    policies = []
    if not objects:
        resource_list = generate_resource_list(s3buckets)
        tmp_list1 = []
        while len(resource_list) > 0:
            tmp_list2 = []
            while getsizeof(tmp_list2) < (6000 - 343):
                for i in range(len(resource_list)):
                    tmp_list2.append(resource_list.pop())
            tmp_list1.append(tmp_list2)

        for item in tmp_list1:
            ipaas_policy = {
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
                            "Resource": item,
                        },
                    ],
                }
            policies.append(ipaas_policy)

    else:
    # ipaas_policy template is 364 bytes when the dict is represented as a string
        resource_list = generate_resource_list(s3buckets, objects=True)
        tmp_list1 = []
        while len(resource_list) > 0:
            tmp_list2 = []
            while getsizeof(tmp_list2) < (6000 - 343):
                for i in range(len(resource_list)):
                    tmp_list2.append(resource_list.pop())
            tmp_list1.append(tmp_list2)

        for item in tmp_list1:
            ipaas_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
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
                            "Resource": item,
                        },
                    ],
                }
            policies.append(ipaas_policy)

    return policies

def detach_role_policy(role_name, policy_arn):
    """detach_role_policy takes a role name and a policy ARN as parameters and detaches that policy from that role."""
    response = ""
    try:
        response = iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    except ClientError as error_client:
        logger.error("ClientError from botocore.exceptions raised when attempting s3.BucketTagging().tag_set")
        logger.error("Error: %s", error_client)
        return (1, response)
    except Exception as error_exception:
        logger.error("General Exception caught")
        logger.error("Error: %s", error_exception)
        return (2, response)

    return 0

def delete_policy(policy_arn):
    """delete_policy takes a policy ARN as a parameter and deletes that policy."""
    response = ""
    try:
        response = iam.list_policy_versions(PolicyArn=policy_arn)
        for policy_version in response["Versions"]:
            if policy_version["IsDefaultVersion"]:
                continue
            response = iam.delete_policy_version(
                PolicyArn=policy_arn, VersionId=policy_version["VersionId"]
            )
        response = iam.delete_policy(PolicyArn=policy_arn)
    except ClientError as error_client:
        logger.error("ClientError from botocore.exceptions raised when attempting s3.BucketTagging().tag_set")
        logger.error("Error: %s", error_client)
        return (1, response)
    except Exception as error_exception:
        logger.error("General Exception caught")
        logger.error("Error: %s", error_exception)
        return (2, response)

    return 0

def create_policy(name, description, policy):
    """create_policy takes a policy name, description, and policy data object (from generate_policy()) and creates a policy via iam."""
    response=""
    try:
        response = iam.create_policy(
            PolicyName=name,
            PolicyDocument=json.dumps(policy),
            Description=description,
            Tags=[
                {"Key": "Technical_Owner", "Value": "dis"},
                {"Key": "Charge_Code", "Value": "15445"},
            ],
        )
    except ClientError as error_client:
        logger.error("ClientError from botocore.exceptions raised when attempting s3.BucketTagging().tag_set")
        logger.error("Error: %s", error_client)
        return (1, response)
    except Exception as error_exception:
        logger.error("General Exception caught")
        logger.error("Error: %s", error_exception)
        return (2, response)

    return 0

def lambda_handler(event, context):
    """lambda_handler is the main function and provides the execution order for the module."""

    resource = boto3.resource("iam")
    acc_id = boto3.client("sts").get_caller_identity().get("Account")
    policy_prefix = "arn:aws:iam::" + acc_id + ":policy/dis-managed-ipaas"
    role_name = "dis-s3-bucket-cross-account-access"
    role = resource.Role(role_name)


    ipaas_write_buckets = get_buckets(buckets, "write")
    ipaas_write_buckets_policies = generate_policy(ipaas_write_buckets)
    ipaas_write_objects_policies = generate_policy(ipaas_write_buckets, objects=True)

    ipaas_read_buckets = get_buckets(buckets, "read")
    ipaas_read_buckets_policies = generate_policy(ipaas_read_buckets)
    ipaas_read_objects_policies = generate_policy(ipaas_read_buckets, objects=True)


    attached_policies = get_role_policies(role_name, policy_prefix)
    for policy in attached_policies:
        if detach_role_policy(role_name, policy["PolicyArn"]) == 0:
            delete_policy(policy["PolicyArn"])
        else:
            logger.error("Detach role policy unsuccessful. Will not delete policy: %s.", policy["PolicyName"])


    count = 0
    for buckets_policy, objects_policy in zip_longest(ipaas_write_buckets_policies, ipaas_write_objects_policies):
        count += 1
        if buckets_policy is not None:
            create_policy("%s-write-buckets-policy-%s" % (policy_prefix, count), "Write bucket policy for ipaas managed by dis lambda #%s" % count, buckets_policy)
            role.attach_policy(PolicyArn="%s-write-buckets-policy-%s" % (policy_prefix, count))
        if objects_policy is not None:
            create_policy("%s-write-objects-policy-%s" % (policy_prefix, count), "Write objects policy for ipaas managed by dis lambda #%s" % count, buckets_policy)
            role.attach_policy(PolicyArn="%s-write-objects-policy-%s" % (policy_prefix, count))

    count = 0
    for buckets_policy, objects_policy in zip_longest(ipaas_read_buckets_policies, ipaas_read_objects_policies):
        count += 1
        if buckets_policy is not None:
            create_policy("%s-read-buckets-policy-%s" % (policy_prefix, count), "Read bucket policy for ipaas managed by dis lambda #%s" % count, buckets_policy)
            role.attach_policy(PolicyArn="%s-read-buckets-policy-%s" % (policy_prefix, count))
        if objects_policy is not None:
            create_policy("%s-read-objects-policy-%s" % (policy_prefix, count), "Read objects policy for ipaas managed by dis lambda #%s" % count, buckets_policy)
            role.attach_policy(PolicyArn="%s-read-objects-policy-%s" % (policy_prefix, count))
