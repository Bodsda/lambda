#! /usr/bin/env python3

"""Module to cleanup attached or unattached role policies created by lambda.py
such as when the bytes_available has been set comically low and now you have
several hundred unattached policies. 
"""

import argparse
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("dis-aws-cross-account-s3-access")
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description="""Cleanup lambda.py policies by deleting them from AWS via the boto3 package. 
Note: This will use the AWS credentials of your current console session. Ensure you are in the correct environment before running.""",
                                 prog="lambda-cleanup.py", usage="python %(prog)s [options]",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-a", "--attached", help="Targets attached policies only",
                    action="store_true")
parser.add_argument("-u", "--unattached", help="Targets unattached policies only",
                    action="store_true")
parser.add_argument("-b", "--both", help="Targets both attached and unattached policies",
                    action="store_true")
args = parser.parse_args()




def detach_role_policy(role_name, policy_arn):
    """detach_role_policy takes a role name and a policy ARN as parameters
    and detaches that policy from that role.

    Returns 0 if successful.
    """
    response = ""  # Defining response outside the try/except due to pylint E0601
    try:
        response = iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        logger.debug(
            "detach_role_policy: Debug: Policy detached: %s from role %s",
            policy_arn,
            role_name,
        )

    except ClientError as error_client:
        logger.error(
            "detach_role_policy: ClientError from botocore.exceptions raised when \
                attempting iam.detach_role_policy in detach_role_policy()"
        )
        logger.error("detach_role_policy: Error: detach_role_policy: %s", error_client)
        return (1, response)
    except Exception as error_exception:
        logger.error("detach_role_policy: General Exception caught")
        logger.error("detach_role_policy: Error: %s", error_exception)
        return (2, response)

    return 0


def delete_policy(policy_arn):
    """delete_policy takes a policy ARN as a parameter and deletes that
    policy.

    Returns 0 if successful.
    """
    try:
        response = iam.list_policy_versions(PolicyArn=policy_arn)
        for policy_version in response["Versions"]:
            if policy_version["IsDefaultVersion"]:
                continue
            response = iam.delete_policy_version(
                PolicyArn=policy_arn, VersionId=policy_version["VersionId"]
            )
        response = iam.delete_policy(PolicyArn=policy_arn)
        logger.debug("delete_policy: Debug: Policy deleted: %s", policy_arn)

    except ClientError as error_client:
        logger.error(
            "delete_policy: ClientError from botocore.exceptions raised when \
                attempting iam.list_policy_version OR iam.delete_policy_version OR\
                iam.delete_policy in delete_policy()"
        )
        logger.error("Error: delete_policy: %s", error_client)
        return (1, response)
    except Exception as error_exception:
        logger.error("delete_policy: General Exception caught")
        logger.error("delete_policy: Error: %s", error_exception)
        return (2, response)


    return 0


def main(aub):
    policies = iam.list_policies()
    for policy in policies["Policies"]:
        if policy_prefix in policy["Arn"]:
            if "read-buckets-policy" in policy["Arn"] or\
                    "read-objects-policy" in policy["Arn"] or\
                    "write-buckets-policy" in policy["Arn"] or\
                    "write-objects-policy" in policy["Arn"]:
                if aub == "a":
                    if policy["AttachmentCount"] == 1:
                        detach_role_policy(role_name, policy["Arn"])
                        logger.log(30, "Policy detached: %s, %s" % (policy["PolicyName"], policy["Arn"]))
                        delete_policy(policy["Arn"])
                        logger.log(30, "Policy deleted: %s, %s" % (policy["PolicyName"], policy["Arn"]))
                elif aub == "u":
                    if policy["AttachmentCount"] == 0:
                        delete_policy(policy["Arn"])
                        logger.log(30, "Policy deleted: %s, %s" % (policy["PolicyName"], policy["Arn"]))
                elif aub == "b":
                    if policy["AttachmentCount"] == 1:
                        detach_role_policy(role_name, policy["Arn"])
                        logger.log(30, "Policy detached: %s, %s" % (policy["PolicyName"], policy["Arn"]))
                        delete_policy(policy["Arn"])
                        logger.log(30, "Policy deleted: %s, %s" % (policy["PolicyName"], policy["Arn"]))
                    if policy["AttachmentCount"] == 0:
                        delete_policy(policy["Arn"])
                        logger.log(30, "Policy deleted: %s, %s" % (policy["PolicyName"], policy["Arn"]))




iam = boto3.client("iam")
acc_id = boto3.client("sts").get_caller_identity().get("Account")
policy_prefix = "arn:aws:iam::" + acc_id + ":policy/dis-managed-ipaas"
role_name = "dis-s3-bucket-cross-account-access"

if args.attached:
    main("a")
elif args.unattached:
    main("u")
elif args.both:
    main("b")
else:
    parser.print_help()
