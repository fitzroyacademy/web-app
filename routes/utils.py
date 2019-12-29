import json

from flask import jsonify

from dataforms import ReorderForm


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
