import hashlib
import io
import json
import os
from datetime import datetime

import boto3
from PIL import Image
from flask import current_app, jsonify

from dataforms import ReorderForm

ALLOWED_MIMETYPES = ["png", "jpg", "jpeg", "gif"]
THUMBNAIL_SIZES = {
    "cover": (800, 450),
    "square_s": (128, 128),
    "square_m": (256, 256),
    "square_l": (512, 512),
}

CLOUD_FRONT_URL = "http://assets.alpha.new.fitzroyacademy.com/"


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

    if not file:
        return None

    ext = file.content_type.split("/")[-1]
    if ext not in ALLOWED_MIMETYPES:
        return ""

    now = datetime.now()
    im = Image.open(file)
    im.thumbnail(THUMBNAIL_SIZES[thumbnail_type])

    filename = "{}_{}_thumb_{}.{}".format(
        now.strftime("%Y-%m-%d-%H-%M-%S-%f"),
        hashlib.md5(file.read()).hexdigest(),
        "x".join("{}".format(n) for n in THUMBNAIL_SIZES[thumbnail_type]),
        ext,
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

    form = ReorderForm(request.form)

    if request.method == "POST" and form.validate():
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

        # Let's check if numbers are correct. In addition make sure that intro elements are excluded from reordering.
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


def retrieve_wistia_id(url):

    url_parts = url.split("wistia.com/medias/")
    if len(url_parts) > 0:
        external_id = url_parts[1].split("/")[0]
        return external_id

    return ""


def find_segment_barrier(current_user, course):
    segments = course.get_ordered_segments(only_barriers=True)
    for segment in segments:
        segment.user = current_user
        if not segment.can_view() and not segment.is_hidden_segment():
            return segment

    return None


def get_session_data(session_obj, key):
    return json.loads(session_obj.get(key, "{}"))


def set_session_data(session_obj, key, data):
    session_obj[key] = json.dumps(data)
