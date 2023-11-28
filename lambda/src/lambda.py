"""Module to detach, delete and re-create permission policies for
s3 bucket and s3 object (files) access
"""
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


# ToDo: review all docstrings - does our generated pydoc
#  describe everything well enough?
def get_buckets(s3buckets, rw_tag):
    """get_buckets takes a list of s3 buckets and attempts to fetch the TagSet (if the bucket has any tags attached)

    For each bucket found, if the TagSet has the "ipaas_transfer_enabled" tag, with a value set to either 'read" or
    "write", that buckets ARN is added to a dictionary called ipaas_buckets - ready for further processing.
    """
    ipaas_buckets = []

    for bucket in s3buckets:
        try:
            tag_set = s3.BucketTagging(bucket.name).tag_set
        except ClientError as error_client:
            if error_client.response["Error"]["Code"] == "NoSuchTagSet":
                logger.debug("Debug: Bucket %s has no tags set", bucket.name)
                continue
            logger.error("Error: Unknown client error occurred: %s", error_client)
            continue

        except Exception as error_exception:
            logger.error("Error: Unknown error occurred: %s", error_exception)

            continue

        for item in tag_set:
            if item["Key"] == "ipaas_transfer_enabled" and item["Value"] == rw_tag:
                ipaas_buckets.append(bucket.name)
                logger.debug(
                    "Debug: Bucket %s found with tag ipaas_transfer_enabled:%s",
                    bucket.name,
                    rw_tag,
                )

    return ipaas_buckets


def get_role_policies(role_name, role_prefix):
    """get_role_policies accepts a role name and a role prefix, then returns
    a list of dictionary objects that contain that policy filtered by prefix
    """
    filtered_policies = []
    try:
        response = iam.list_attached_role_policies(RoleName=role_name)
        for policy in response["AttachedPolicies"]:
            if role_prefix in policy["PolicyArn"]:
                filtered_policies.append({policy["PolicyName"]: policy["PolicyArn"]})
    except Exception as error_exception:
        logger.error("General Exception caught")
        logger.error("Error: %s", error_exception)

    return filtered_policies


def generate_resource_list(s3buckets, objects=False):
    """generate_resource_list takes a list of s3 buckets and optionally a
    parameter to indicate if you want the resource list to return objects
    instead of buckets.
    """
    resource_list = []

    for item in s3buckets:
        if not objects:
            resource_list.append("arn:aws:s3:::" + item)
        else:
            resource_list.append("arn:aws:s3:::" + item + "/*")

    return resource_list


def generate_policy(s3buckets, objects=False):
    """generate_policy takes a list of s3 buckets and optionally a parameter
    to indicate if you want the resultant policy data to be for buckets or
    objects.

    There is a hard limit of 6i44 Bytes (or 6k characters) for individual AWS policies
    this module monitors the size of the policy string by assessing the length of each
    ARN before adding it.
    see this page for detail https://repost.aws/knowledge-center/iam-increase-policy-size

    Returns a dictionary of policy ARNs


    bytes_available = 5500       # Available bytes to be used by ARNs
    remaining = bytes_available  # Remaining bytes counter initially set to bytes_available and
                                 # then decremented in the following loops

    padding = 3                  # When assessing ARN length there is some additional unidentified
                                 # characters added at some point. This variable causes the ARN to
                                 # be assessed as longer than it is by whatever the variable value
                                 # is. This allows us to use 6144 as the bytes_available, in line
                                 # with AWS policy limits, instead of an arbitrarily smaller value
                                 # that would have no real meaning.
                                 # it might work =2 but does work =3
    """

    policies = []
    bytes_available = 3000  # Available bytes to be used by ARNs (6144)
    padding = 3  # See docstring

    if not objects:
        filename = "buckets.json"
        arn_type = "buckets"
        resource_list = generate_resource_list(s3buckets)
    else:
        filename = "objects.json"
        arn_type = "objects"
        resource_list = generate_resource_list(s3buckets, objects=True)

    with open(filename, encoding="utf-8") as handle:
        data = handle.read()
        whitespace = data.count(" ") + data.count("\t") + data.count("\n")
        chars = len(data) - whitespace

    remaining = bytes_available - chars
    tmp_list1 = []  # list of correctly sized policy resources
    tmp_list2 = []  # temporary list to test if the policy will become too large

    for i in resource_list:
        if (remaining - len(i) - padding) > 0:
            logger.debug(
                "DEBUG: Appending %s ARN to tmp_list2. remaining variable = %s,\
                    size = %s",
                arn_type,
                remaining,
                len(i),
            )
            remaining = remaining - len(i) - padding
            tmp_list2.append(i)
        else:  # no room for additional arns
            tmp_list1.append(tmp_list2)
            logger.debug(
                "DEBUG: Appending %s ARN list to tmp_list1. remaining variable = %s",
                arn_type,
                remaining,
            )
            tmp_list2 = []
            tmp_list2.append(i)  # add the current arn to the freshly emptied list_2
            remaining = bytes_available - chars
            remaining = remaining - len(i) - padding

    if len(tmp_list2) > 0:
        tmp_list1.append(tmp_list2)
        logger.debug(
            "DEBUG: Appending final %s ARN list to tmp_list1. remaining variable = %s",
            arn_type,
            remaining,
        )

    for item in tmp_list1:
        with open(filename, encoding="utf-8") as handle:
            ipaas_policy = json.load(handle)
            ipaas_policy["Statement"][0]["Resource"] = item
        policies.append(ipaas_policy)

    return policies


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
                attempting s3.BucketTagging().tag_set in detach_role_policy()"
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
                attempting s3.BucketTagging().tag_set in delete_policy()"
        )
        logger.error("Error: delete_policy: %s", error_client)
        return (1, response)
    except Exception as error_exception:
        logger.error("delete_policy: General Exception caught")
        logger.error("delete_policy: Error: %s", error_exception)
        return (2, response)

    return 0


def create_policy(name, description, policy):
    """create_policy takes a policy name, description, and policy data object
    (from generate_policy()) and creates a policy via iam.

    Returns 0 if successful.
    """
    response = ""  # Defining response outside the try/except due to pylint E0601
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
        logger.debug("create_policy: Debug: Policy created: %s", name)

    except ClientError as error_client:
        logger.error(
            "create_policy: ClientError from botocore.exceptions raised when \
                attempting s3.BucketTagging().tag_set in create_policy()"
        )
        logger.error("create_policy: Error: %s", error_client)
        logger.error("Policy: %s", policy)
        return (1, response)
    except Exception as error_exception:
        logger.error("create_policy: General Exception caught")
        logger.error("create_policy: Error: %s", error_exception)
        return (2, response)

    return 0


def lambda_handler(event, context):
    """lambda_handler is the main function and provides the execution order
    for the module.
    """
    resource = boto3.resource("iam")
    acc_id = boto3.client("sts").get_caller_identity().get("Account")
    policy_prefix = "arn:aws:iam::" + acc_id + ":policy/dis-managed-ipaas"
    role_name = "dis-s3-bucket-cross-account-access"
    role = resource.Role(role_name)

    # make lists
    ipaas_write_buckets = get_buckets(buckets, "write")
    ipaas_write_buckets_policies = generate_policy(ipaas_write_buckets)
    ipaas_write_objects_policies = generate_policy(ipaas_write_buckets, objects=True)

    ipaas_read_buckets = get_buckets(buckets, "read")
    ipaas_read_buckets_policies = generate_policy(ipaas_read_buckets)
    ipaas_read_objects_policies = generate_policy(ipaas_read_buckets, objects=True)

    # iterate through the list of policies attached to the dis-s3-bucket-cross-account-access role
    attached_policies = get_role_policies(role_name, policy_prefix)
    for policy in attached_policies:
        policy_arn = next(iter(policy.values()))
        if (
            detach_role_policy(role_name, policy_arn) == 0
        ):  # success code returned by detach_role_policy function
            delete_policy(policy_arn)
        else:
            logger.error(
                "Detach role policy unsuccessful. Will not delete \
                    policy: %s.",
                policy_arn,
            )

    count = 0
    write_buckets_count = 0
    write_objects_count = 0
    for buckets_policy, objects_policy in zip_longest(
        ipaas_write_buckets_policies, ipaas_write_objects_policies
    ):
        count += 1
        if buckets_policy is not None:
            write_buckets_count += 1
            # if write_buckets_count <= 10:
            create_policy(
                f"dis-managed-ipaas-write-buckets-policy-{count}",
                "Write bucket policy for ipaas managed by dis lambda #{count}",
                buckets_policy,
            )
            try:
                role.attach_policy(
                    PolicyArn=f"{policy_prefix}-write-buckets-policy-{count}"
                )
            except ClientError as client_error:
                if client_error.response["Error"]["Code"] == "LimitExceededException":
                    logger.error(
                        "ERROR: write_buckets: The number of Policies created has exceeded your AWS attached policy quota \
                        Error: %s",
                        client_error,
                    )
            # else:
            #     logger.error(
            #         "ERROR: Policy count would exceed 10. No further write bucket policies\
            #             will be created. Suggest requesting a quota increase"
            #     )

        if objects_policy is not None:
            # if write_objects_count <= 10:
            write_objects_count += 1
            create_policy(
                f"dis-managed-ipaas-write-objects-policy-{count}",
                "Write objects policy for ipaas managed by dis lambda #{count}",
                objects_policy,
            )
            try:
                role.attach_policy(
                    PolicyArn=f"{policy_prefix}-write-objects-policy-{count}"
                )
            except ClientError as client_error:
                if client_error.response["Error"]["Code"] == "LimitExceededException":
                    logger.error(
                        "ERROR: write_objects_count: The number of Policies created has exceeded your AWS attached policy quota \
                        Error: %s",
                        client_error,
                    )
            # else:
            #     logger.error(
            #         "ERROR: Policy count would exceed 10. No further write object policies\
            #             will be created. Suggest requesting a quota increase"
            #     )

    # create & attach the new policies
    count = 0
    read_buckets_count = 0
    read_objects_count = 0
    for buckets_policy, objects_policy in zip_longest(
        ipaas_read_buckets_policies, ipaas_read_objects_policies
    ):
        count += 1
        if buckets_policy is not None:
            read_buckets_count += 1
            # if read_buckets_count <= 10:
            create_policy(
                f"dis-managed-ipaas-read-buckets-policy-{count}",
                "Read bucket policy for ipaas managed by dis lambda #{count}",
                buckets_policy,
            )
            try:
                role.attach_policy(
                    PolicyArn=f"{policy_prefix}-read-buckets-policy-{count}"
                )
            except ClientError as client_error:
                if client_error.response["Error"]["Code"] == "LimitExceededException":
                    logger.error(
                        "ERROR: read_buckets_count: The number of Policies created has exceeded your AWS attached policy quota \
                        Error: %s",
                        client_error,
                    )
            # else:
            #     logger.error(
            #         "ERROR: Policy count would exceed 10. No further read bucket policies\
            #             will be created. Suggest requesting a quota increase"
            #     )

        if objects_policy is not None:
            read_objects_count += 1
            # if read_objects_count <= 10:
            create_policy(
                f"dis-managed-ipaas-read-objects-policy-{count}",
                "Read objects policy for ipaas managed by dis lambda #{count}",
                buckets_policy,
            )
            try:
                role.attach_policy(
                    PolicyArn=f"{policy_prefix}-read-objects-policy-{count}"
                )
            except ClientError as client_error:
                if client_error.response["Error"]["Code"] == "LimitExceededException":
                    logger.error(
                        "ERROR: read_objects_count: The number of Policies created has exceeded your AWS attached policy quota \
                        Error: %s",
                        client_error,
                    )
            # else:
            #     logger.error(
            #         "ERROR: Policy count would exceed 10. No further read object policies\
            #             will be created. Suggest requesting a quota increase"
            #     )
