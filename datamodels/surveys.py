import json
import sqlalchemy as sa

from .base import Base
from .enums import SurveyTypeEnum
from .survey_templates import SURVEYS_TEMPLATES


class Survey(Base):
    __abstract__ = True

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
    def _survey_template_definition_checker(cls, survey_template, require_answer=False):
        if not isinstance(survey_template, dict):
            raise ValueError("Survey template must be a dictionary")

        assert "survey_id" in survey_template
        assert "survey_template_version" in survey_template
        assert "question" in survey_template
        assert "min_response_length" in survey_template
        assert isinstance(survey_template["min_response_length"], int)
        assert "survey_type" in survey_template
        assert "survey_type_name" in survey_template
        assert "survey_type_description" in survey_template
        assert "survey_type_icon" in survey_template
        assert "survey_type_icon_type" in survey_template
        assert survey_template["survey_type"] in cls.list_survey_types()
        if survey_template["survey_type"] == "emoji":
            assert "choice_questions" in survey_template
            for question in survey_template["choice_questions"]:
                assert "icon" in question
                assert "icon_type" in question
                assert "single_word" in question
                assert "short_sentence" in question
                assert "id" in question
        if survey_template["survey_type"] == "points_scale":
            assert "right_label" in survey_template
            assert "left_label" in survey_template
            assert "scale_start" in survey_template
            assert isinstance(survey_template["scale_start"], int)
            assert "scale_stop" in survey_template
            assert isinstance(survey_template["scale_stop"], int)

        if require_answer:
            assert "answer_template" in survey_template
            cls._survey_answer_template_definition_checker(
                survey_template.pop("answer_template"), survey_template["survey_type"]
            )

    @classmethod
    def _survey_answer_template_definition_checker(cls, answer_template, survey_type):
        assert "reason_response" in answer_template
        if survey_type in ["emoji", "points_scale"]:
            assert "chosen_answer" in answer_template

    def get_survey_type(self):
        return self.survey_type.name if self.survey_type else ""

    def save_questions_template(self, survey_data):
        self._survey_template_definition_checker(
            survey_data, require_answer=not self.questions_template
        )

        answer_template = survey_data.pop("answer_template", None)
        if answer_template:
            self.answer_template = json.dumps(answer_template)
        self.questions_template = json.dumps(survey_data)

    def get_questions_template(self):
        if not self.questions_template:
            raise ValueError("No questions template added")
        template = json.loads(self.questions_template)
        self._survey_template_definition_checker(template)

        return template

    def get_answer_template(self):
        if not self.answer_template:
            raise ValueError("No answer template added")
        if not self.survey_type:
            raise ValueError("Survey type not defined")
        template = json.loads(self.answer_template)
        self._survey_answer_template_definition_checker(template, self.survey_type.name)

        return template
