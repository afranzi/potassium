import json

import boto3

from potassium.config.secrets.aws import get_aws_region


def set_up_secret(secret_name: str, content: dict, region=get_aws_region()):
    conn = boto3.client("secretsmanager", region_name=region)
    conn.create_secret(Name=secret_name, SecretString=json.dumps(content))
