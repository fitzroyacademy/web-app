import json
import sqlalchemy as sa

from .base import BaseModel
from .enums import SurveyTypeEnum
from .survey_templates import SURVEYS_TEMPLATES


class Survey(BaseModel):
    __abstract__ = True
    __survey_template = {}

    survey_type = sa.Column(sa.Enum(SurveyTypeEnum), nullable=True, default=None)
    questions_template = sa.Column(sa.String, default="")
    answer_template = sa.Column(sa.String, default="")

    @staticmethod
    def list_survey_types():
        return [t.name for t in SurveyTypeEnum]

    @staticmethod
    def list_types_templates():
        return SURVEYS_TEMPLATES

    @classmethod
    def get_base_template_by_id(cls, survey_id):
        templates = cls.list_types_templates()
        for template in templates:
            if template["survey_id"] == survey_id:
                return template.copy()  # we don't want to make a reference

    @classmethod
    def _survey_template_definition_checker(cls, survey_template, require_answer=False):
        if not isinstance(survey_template, dict):
            raise ValueError("Survey template must be a dictionary")

        assert "survey_id" in survey_template
        assert "survey_template_version" in survey_template
        assert "question" in survey_template
        assert "free_text_minlength" in survey_template
        assert isinstance(
            survey_template["free_text_minlength"], int
        ), "Free text length should be integer"
        assert "survey_type" in survey_template
        assert "survey_type_name" in survey_template
        assert "survey_type_description" in survey_template
        assert "survey_type_icon" in survey_template
        assert "survey_type_icon_type" in survey_template
        assert survey_template["survey_type"] in cls.list_survey_types()
        if survey_template["survey_type"] == "emoji":
            assert "choice_questions" in survey_template
            assert "free_text_entry" in survey_template
            assert "free_text_require" in survey_template
            for question in survey_template["choice_questions"]:
                assert "icon" in question
                assert "icon_type" in question
                assert "single_word" in question
                assert "short_sentence" in question
                assert "id" in question
        if survey_template["survey_type"] == "points_scale":
            assert "free_text_entry" in survey_template
            assert "free_text_require" in survey_template
            assert "right_label" in survey_template
            assert "left_label" in survey_template
            assert "scale_start" in survey_template
            assert isinstance(
                survey_template["scale_start"], int
            ), "Scale start should be integer"
            assert "scale_stop" in survey_template
            assert isinstance(
                survey_template["scale_stop"], int
            ), "Scale stop should be integer"

        if require_answer:
            assert "answer_template" in survey_template
            cls._survey_answer_template_definition_checker(
                survey_template.pop("answer_template"), survey_template["survey_type"]
            )

    @classmethod
    def _survey_answer_template_definition_checker(cls, answer_template, survey_type):
        assert "free_text_response" in answer_template
        if survey_type in ["emoji", "points_scale"]:
            assert "chosen_answer" in answer_template

    def get_survey_type(self):
        return self.survey_type.name if self.survey_type else ""

    def set_survey_type(self, survey_type):
        self.survey_type = getattr(SurveyTypeEnum, survey_type, "plain_text")

    def save_questions_template(self, survey_data):
        self._survey_template_definition_checker(
            survey_data, require_answer=not self.questions_template
        )

        self.set_survey_type(survey_data["survey_type"])

        answer_template = survey_data.pop("answer_template", None)
        if answer_template:
            self.answer_template = json.dumps(answer_template)
        self.questions_template = json.dumps(survey_data)

    def get_questions_template(self):
        if self.__survey_template:
            return self.__survey_template
        else:
            if not self.questions_template:
                raise ValueError("No questions template added")
            self.__survey_template = json.loads(self.questions_template)
            self._survey_template_definition_checker(self.__survey_template)

        return self.__survey_template

    def get_answer_template(self):
        if not self.answer_template:
            raise ValueError("No answer template added")
        if not self.survey_type:
            raise ValueError("Survey type not defined")
        template = json.loads(self.answer_template)
        self._survey_answer_template_definition_checker(template, self.survey_type.name)

        return template


class SurveyResponse(BaseModel):
    __abstract__ = True

    id = sa.Column(sa.Integer, primary_key=True)
    answers = sa.Column(sa.String, default="")
    survey = None
    user = None

    __serialize_answers = None
    __is_data_valid = False

    def validate_data(self, chosen_answer="", free_text=""):
        survey_template = self.survey.get_questions_template()
        if self.survey.survey_type == SurveyTypeEnum.plain_text and not free_text:
            raise ValueError("No response provide")

        if self.survey.survey_type != SurveyTypeEnum.plain_text:
            if survey_template["free_text_require"] and not free_text:
                raise ValueError("No response provide")
            if not chosen_answer:
                raise ValueError("Please choose an answer")

            if self.survey.survey_type == SurveyTypeEnum.emoji:
                if chosen_answer not in [
                    str(q["id"]) for q in survey_template["choice_questions"]
                ]:
                    raise ValueError("Chosen answer is not valid")
            else:
                if chosen_answer not in [
                    str(i)
                    for i in range(
                        survey_template["scale_start"], survey_template["scale_stop"]
                    )
                ]:
                    raise ValueError("Chosen answer is not valid")

        self.__is_data_valid = True
        return self.serialize_answers(chosen_answer=chosen_answer, free_text=free_text)

    def serialize_answers(self, chosen_answer="", free_text=""):
        if not self.__serialize_answers:
            answer_template = self.survey.get_answer_template()
            if "chosen_answer" in answer_template:
                answer_template["chosen_answer"] = chosen_answer

            answer_template["free_text_response"] = free_text
            self.__serialize_answers = answer_template
        return self.__serialize_answers

    def save_response_for_user(self, user):
        if not self.__is_data_valid:
            raise ValueError("Validate data")
        self.user = user
        self.answers = json.dumps(self.__serialize_answers)
        self.save()
