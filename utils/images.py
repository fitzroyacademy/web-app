import requests
import hashlib
import io
import os
from datetime import datetime

import boto3
from PIL import Image
from flask import current_app


ALLOWED_MIMETYPES = ["png", "jpg", "jpeg", "gif"]
THUMBNAIL_SIZES = {
    "cover": (800, 450),
    "square_s": (128, 128),
    "square_m": (256, 256),
    "square_l": (512, 512),
    "standard": (640, 320),
}

CLOUD_FRONT_URL = "http://assets.alpha.new.fitzroyacademy.com/"


def upload_file_to_s3(file, bucket_name="", filename=None):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=current_app.config["S3_KEY"],
        aws_secret_access_key=current_app.config["S3_SECRET"],
        region_name="us-east-2",
    )

    if not bucket_name:
        bucket_name = current_app.config["S3_BUCKET"]

    if not hasattr(file, "filename") and not filename:
        raise ValueError("Provide either filename or file object")

    filename = filename if filename else file.filename

    try:
        s3.upload_fileobj(file, bucket_name, filename)

    except Exception as e:
        print("Something Happened: ", e)
        return ""

    return "{}{}".format(CLOUD_FRONT_URL, filename)


def image_upload_dispatcher(im, filename):
    """
    Dispatch file location depending on the environment (debug, test, staging and production)
    """
    if current_app.config["DEBUG"] or current_app.config["TESTING"]:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        im.save(file_path)
    else:
        b = io.BytesIO()
        im.save(b, im.format)
        b.seek(0)
        filename = upload_file_to_s3(b, filename=filename)

    return filename


def generate_filename(thumbnail_type, file, ext):
    now = datetime.now()
    return "{}_{}_thumb_{}.{}".format(
        now.strftime("%Y-%m-%d-%H-%M-%S-%f"),
        hashlib.md5(file.read()).hexdigest(),
        "x".join("{}".format(n) for n in THUMBNAIL_SIZES[thumbnail_type]),
        ext,
    )


def generate_thumbnail(file, thumbnail_type):

    if not file:
        return None

    ext = file.content_type.split("/")[-1]
    if ext not in ALLOWED_MIMETYPES:
        return ""

    img = Image.open(file)
    img.thumbnail(THUMBNAIL_SIZES[thumbnail_type])

    filename = generate_filename(thumbnail_type, file, ext)
    file_path = image_upload_dispatcher(img, filename)

    return file_path


def fetch_thumbnail_from_wistia(wistia_id, thumbnail_type="standard"):
    url = "http://fast.wistia.net/oembed?url=http://home.wistia.com/medias/{}?embedType=async&videoWidth=640".format(
        wistia_id
    )
    data = requests.get(url).json()
    width, height = THUMBNAIL_SIZES[thumbnail_type]
    url = data["thumbnail_url"].split("?")[0] + "?image_crop_resized={}x{}".format(
        width, height
    )

    try:
        response = requests.get(url)
        file = io.BytesIO(response.content)
        img = Image.open(file)
        filename = generate_filename(thumbnail_type, file, "jpg")
        file_path = image_upload_dispatcher(img, filename)

        return file_path
    except Exception as e:
        print(e)
        return ""
