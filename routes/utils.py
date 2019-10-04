import io
import os
from datetime import datetime

import boto3
from PIL import Image
from flask import current_app, jsonify

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]
THUMBNAILS = {
    "cover": {"name": "800x450", "size": (800, 450)},
    "square_s": {"name": "128x128", "size": (128, 128)},
    "square_m": {"name": "256x256", "size": (256, 256)},
    "square_l": {"name": "512x512", "size": (512, 512)},
}

CLOUD_FRONT_URL = "http://assets.alpha.new.fitzroyacademy.com/"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


def upload_file_to_s3(file, s3, bucket_name, filename=None):

    if not hasattr(file, "filename") and not filename:
        raise ValueError("Provide either filename or file object")

    filename = filename if filename else file.filename

    try:
        s3.upload_fileobj(file, bucket_name, filename)

    except Exception as e:
        print("Something Happened: ", e)
        return ""

    return "{}{}".format(CLOUD_FRONT_URL, filename)


def generate_thumbnail(file, thumbnail_type):
    if not file or not allowed_file(file.filename):
        return ""

    now = datetime.now()
    im = Image.open(file)
    im.thumbnail(THUMBNAILS[thumbnail_type]["size"])

    filename = "{}_thumb_{}.{}".format(
        now.strftime("%Y-%m-%d-%H-%M-%S-%f"),
        THUMBNAILS["cover"]["name"],
        file.filename.rsplit(".", 1)[1],
    )

    if current_app.config["DEBUG"] or current_app.config["TESTING"]:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        im.save(file_path)
    else:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=current_app.config["S3_KEY"],
            aws_secret_access_key=current_app.config["S3_SECRET"],
            region_name="us-east-2",
        )
        b = io.BytesIO()
        im.save(b, im.format)
        b.seek(0)
        filename = upload_file_to_s3(b, s3, current_app.config["S3_BUCKET"], filename)

    return filename


def reorder_items(request, cls, objects):

    if request.method == "POST" and "items_order" in request.form:
        # we should get ordered list of lessons
        items_order = request.form["items_order"]
        if items_order:
            try:
                items_order = [int(e) for e in items_order.split(",")]
            except ValueError:
                return jsonify({"success": False, "message": "Wrong data format"}), 400
        else:
            return (
                jsonify(
                    {"success": False, "message": "Expected ordered list of items"}
                ),
                400,
            )

        # Let's check if numbers are correct
        list_of_objects = [obj.id for obj in objects if obj.order != 0]

        if set(items_order).difference(set(list_of_objects)) or set(
            items_order
        ).difference(set(list_of_objects)):
            return (
                jsonify({"success": False, "message": "Wrong number of items"}),
                400,
            )

        cls.reorder_items(items_order)

        return jsonify({"success": True, "message": "Order updated"})

    return jsonify({"success": False, "message": "No data"}), 400


def clone_model(model, **kwargs):
    """Clone an arbitrary sqlalchemy model object without its primary key values."""
    # Ensure the model’s data is loaded before copying.
    model.id

    table = model.__table__
    non_pk_columns = [k for k in table.columns.keys() if k not in table.primary_key]
    data = {c: getattr(model, c) for c in non_pk_columns}
    data.update(kwargs)

    clone = model.__class__(**data)
    return clone