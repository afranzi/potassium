import json
import re

import boto3
from boto3 import Session
from botocore.exceptions import ClientError
from mypy_boto3_secretsmanager import SecretsManagerClient
from pydantic_settings import BaseSettings, SettingsConfigDict


class AwsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="aws_")

    region: str


def get_aws_region() -> str:
    return AwsSettings().region


def get_region_from_secret(secret_name: str) -> str | None:
    arn_regex = re.compile(
        r"arn:aws:secretsmanager:(?P<region>[\w-]+):(?P<account_id>\d{12}):secret:(?P<secret_name>.+)"
    )
    search_result = arn_regex.search(secret_name)
    search_groups = search_result.groupdict() if search_result else {}
    return search_groups.get("region", None)


def aws_session(region_name: str | None = None) -> Session:
    region_name = region_name or get_aws_region()
    return boto3.session.Session(region_name=region_name)


def secrets_client(region_name: str | None = None) -> SecretsManagerClient:
    return aws_session(region_name).client(service_name="secretsmanager")


def get_secret(secret_name: str) -> dict:
    region_name = get_region_from_secret(secret_name)
    client = secrets_client(region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret_str = get_secret_value_response["SecretString"]
    return json.loads(secret_str)
