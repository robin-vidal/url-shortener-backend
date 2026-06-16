import os
import boto3


def get_ssm_parameter(name: str, with_decryption: bool = False) -> str:
    client = boto3.client("ssm", region_name="us-east-1")
    response = client.get_parameter(Name=name, WithDecryption=with_decryption)
    return response["Parameter"]["Value"]


def get_db_url() -> str:
    # Local dev: use DATABASE_URL env var
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    # Production: fetch from SSM Parameter Store
    host = get_ssm_parameter("/url-shortener/db/host")
    name = get_ssm_parameter("/url-shortener/db/name")
    user = get_ssm_parameter("/url-shortener/db/user")
    password = get_ssm_parameter("/url-shortener/db/password", with_decryption=True)

    return f"postgresql://{user}:{password}@{host}/{name}"
