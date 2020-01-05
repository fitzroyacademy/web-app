import json

from flask import jsonify

from dataforms import ReorderForm
import datamodels


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


class SurveyViewInterface(object):
    """
    Interface that reads and serialize survey data for view.
    """

    def __init__(self, survey_id=None, survey_type=None):
        self.survey_type = survey_type
        self.survey_id = survey_id

    @property
    def free_text_minlength_field_name(self):
        return "free_text_minlength_{}".format(self.survey_id)

    @property
    def free_text_entry_field_name(self):
        return "free_text_entry_{}".format(self.survey_id)

    @property
    def free_text_require_field_name(self):
        return "free_text_require_{}".format(self.survey_id)

    @property
    def left_label_field_name(self):
        return "left_label_{}".format(self.survey_id)

    @property
    def right_label_field_name(self):
        return "right_label_{}".format(self.survey_id)

    def single_word_field_name(self, q_id):
        return "single_word_{}_{}".format(self.survey_id, q_id)

    def short_sentence_field_name(self, q_id):
        return "short_sentence_{}_{}".format(self.survey_id, q_id)

    def read_questions_template_from_view(self, data):
        template = datamodels.Segment.get_base_template_by_id(self.survey_id)

        if template is None:
            return None

        template["question"] = data.get("segment_name")
        self.survey_type = template["survey_type"]
        try:
            template["free_text_minlength"] = int(
                data.get(self.free_text_minlength_field_name, 0)
            )
        except ValueError:
            raise ValueError("Free text length should be integer")

        if self.survey_type == "plain_text":
            template["free_text_minlength"] = (
                100
                if not template["free_text_minlength"]
                else template["free_text_minlength"]
            )
        elif self.survey_type == "emoji":
            template["free_text_entry"] = data.get(self.free_text_entry_field_name, "")
            template["free_text_require"] = (
                data.get(self.free_text_require_field_name, "off") == "on"
            )
            for question in template["choice_questions"]:
                question["single_word"] = data.get(
                    self.single_word_field_name(question["id"])
                )
                question["short_sentence"] = data.get(
                    self.short_sentence_field_name(question["id"])
                )
        elif self.survey_type == "points_scale":
            template["free_text_entry"] = data.get(self.free_text_entry_field_name, "")
            template["free_text_require"] = (
                data.get(self.free_text_require_field_name, "off") == "on"
            )
            template["left_label"] = data.get(self.left_label_field_name, "")
            template["right_label"] = data.get(self.right_label_field_name, "")

        return template

    def serialize_survey_data_for_view(self, data):
        self.survey_id = data["survey_id"]
        survey_data = {self.free_text_minlength_field_name: data["free_text_minlength"]}

        if self.survey_type == "emoji":
            survey_data[self.free_text_entry_field_name] = data["free_text_entry"]
            survey_data[self.free_text_require_field_name] = data["free_text_require"]
            survey_data["choice_questions"] = [
                {
                    self.single_word_field_name(question["id"]): question[
                        "single_word"
                    ],
                    self.short_sentence_field_name(question["id"]): question[
                        "short_sentence"
                    ],
                }
                for question in data["choice_questions"]
            ]
        elif self.survey_type == "points_scale":
            survey_data[self.free_text_entry_field_name] = data["free_text_entry"]
            survey_data[self.free_text_require_field_name] = data["free_text_require"]
            survey_data[self.left_label_field_name] = data["left_label"]
            survey_data[self.right_label_field_name] = data["right_label"]

        return survey_data
