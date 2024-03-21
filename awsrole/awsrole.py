#!/usr/bin/env python3
"""
Generate temporary credentials and Login URL for a given AWS role.
"""

import argparse
import json
import logging
import os
import sys
from urllib import parse
from urllib import request
from typing import Dict, Any, Callable

import boto3 # type: ignore
from botocore.exceptions import NoCredentialsError # type: ignore
from botocore.client import BaseClient # type: ignore


DEF_DURATION = 43200  # 12h


def get_my_account(sts: BaseClient) -> str:
    """
    Retrieve the AWS account ID of currently logged-in IAM user.
    """
    try:
        id_resp = sts.get_caller_identity()
    except NoCredentialsError:
        logging.error("No AWS credentials found. Run `aws configure` first.")
        sys.exit(1)
    return id_resp["Account"]


def sts_assume_role(sts: BaseClient, role_name: str) -> Dict[str, Any]:
    """
    Use the STS:AssumeRole API to generate temporary credentials for a role
    """
    # Clear up temporary creds from the envvars, to enable repeated use
    if "AWS_SESSION_TOKEN" in os.environ:
        os.environ.pop("AWS_ACCESS_KEY_ID", None)
        os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
        os.environ.pop("AWS_SESSION_TOKEN", None)
    try:
        as_role = sts.assume_role(
            RoleArn=role_name,
            RoleSessionName="AssumeRoleSession",
        )
    except NoCredentialsError:
        logging.error("No AWS credentials found. Run `aws configure` first.")
        sys.exit(1)
    creds = {}
    creds["sessionId"] = as_role.get("Credentials").get("AccessKeyId")
    creds["sessionKey"] = as_role.get("Credentials").get("SecretAccessKey")
    creds["sessionToken"] = as_role.get("Credentials").get("SessionToken")
    return creds


def generate_url(creds: Dict[str, Any], duration: int) -> str:
    """
    Use temporary credentials to generate a sign-in URL through the Federation
    AWS endpoint
    """
    params = {
        "Action": "getSigninToken",
        "SessionDuration": str(duration),
        "Session": json.dumps(creds),
    }

    url = "https://signin.aws.amazon.com/federation?" + parse.urlencode(params)
    with request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        token = data["SigninToken"]

    urlparams = {
        "Action": "login",
        "Issue": "NA",
        "Destination": "https://console.aws.amazon.com/",
        "SigninToken": token,
    }
    lparams = parse.urlencode(urlparams)
    login_url = "https://signin.aws.amazon.com/federation?{}".format(lparams)
    return login_url


# Custom function to check if the value is within the desired range
def int_range(min_val: int, max_val: int) -> Callable[[str], int]:
    """
    Integer range check for argparse parameters
    """

    def check_range(value):
        ivalue = int(value)
        if ivalue < min_val or ivalue > max_val:
            raise argparse.ArgumentTypeError(
                f"{value} is not in the range [{min_val}, {max_val}]"
            )
        return ivalue

    return check_range

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", type=str, help="Role to assume")
    parser.add_argument(
        "-a",
        "--account",
        type=str,
        default="",
        help="Specify an account ID, instead of auto-discovering it",
    )
    parser.add_argument(
        "-t",
        "--time",
        type=int_range(3600, 43200),
        default=DEF_DURATION,
        help="Temp credentials validity in seconds (default: %s)" % DEF_DURATION,
    )
    return parser.parse_args()

def main():
    args = parse_args()
    sts = boto3.client("sts")

    account = args.account or get_my_account(sts)
    role_arn = "arn:aws:iam::{}:role/{}".format(account, args.role)
    creds = sts_assume_role(sts, role_arn)

    print(
        """# Export following vars in your shell for API/CLI access:
    export AWS_ACCESS_KEY_ID={sessionId}
    export AWS_SECRET_ACCESS_KEY={sessionKey}
    export AWS_SESSION_TOKEN={sessionToken}
    """.format(**creds)
    )
    login_url = generate_url(creds, args.time)
    print("# Login URL: {}".format(login_url))

if __name__ == "__main__":
    main()
