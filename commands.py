import boto3
import click
from botocore.exceptions import ClientError
from flask import Blueprint, current_app

from utils.database import reseed
from utils.email import send_email

bp = Blueprint("commands", __name__)


@bp.cli.command("reseed-database")
def reseed_database():
    reseed()


@bp.cli.command("test-email")
@click.argument("email_to")
@click.argument("email_from")
@click.argument("subject")
@click.argument("body")
def test_email(email_to, email_from, subject, body):
    send_email(email_to, email_from, subject, body)


@bp.cli.command("test-s3")
@click.argument("file_name")
def test_s3(file_name):
    upload_to_s3(file_name)


def upload_to_s3(file_name, object_name=None):
    bucket_name = current_app.config.get("S3_BUCKET")

    if object_name is None:
        object_name = file_name
    if bucket_name is None:
        current_app.logger.warn(
            "No S3_BUCKET specified in environment variables. File name to upload: {}".format(
                object_name
            )
        )
        return True
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        current_app.logger.error(e)
        return False
    return True
