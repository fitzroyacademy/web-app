import json
import sqlalchemy as sa

from .base import Base
from .enums import SurveyTypeEnum
from .survey_templates import SURVEYS_TEMPLATES


class Survey(Base):
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
