import unittest
import datamodels
from app import app

from datamodels.enums import SurveyTypeEnum
from datamodels.segments import Segment
from .utils import ObjectsGenerator


class TestSegments(ObjectsGenerator, unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

            self.survey_1 = {
                "survey_id": "some_long_id",
                "survey_template_version": "1.0",
                "question": "How do you feel about the course?",
                "free_text_minlength": 30,
                "free_text_entry": "Why do you feel that way?",
                "free_text_require": False,
                "survey_type": "emoji",
                "survey_type_name": "Happiness",
                "survey_type_description": "3 faces, from angry to happy, with labels.",
                "survey_type_icon": "https://some-fancy-url-with-very-fancy-icon",
                "survey_type_icon_type": "url",
                "answer_template": {"survey_id": "",
                                    "free_text_response": "",
                                    "chosen_answer": ""},
                "choice_questions": [{
                    "icon": "https://again-again-and-so-on.png",
                    "icon_type": "url",
                    "single_word": "Terrible",
                    "short_sentence": "I feel terrible",
                    "id": ""
                }, {
                    "icon": "https://again-again-and-so-on-2.png",
                    "icon_type": "url",
                    "single_word": "Bad",
                    "short_sentence": "I feel pretty bad",
                    "id": ""
                }, {
                    "icon": "https://again-again-and-so-on-3.png",
                    "icon_type": "url",
                    "single_word": "Amazing",
                    "short_sentence": "OMG I feel amazing!",
                    "id": ""
                }]
            }

            self.survey_types = ["plain_text", "points_scale", "emoji"]

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def test_list_survey_types_ids(self):
        types_ids = Segment.list_survey_types()
        self.assertTrue(isinstance(types_ids, list))
        self.assertEqual(len(types_ids), len(set(types_ids)))

    def test_get_survey_type(self):
        survey = Segment(survey_type=SurveyTypeEnum.plain_text)
        self.assertEqual(survey.get_survey_type(), "plain_text")

    def test_list_survey_types_templates(self):
        """
        For each unique template ID there should be a corresponding template.
        Each template should be a valid template provided as JSON object.
        """
        templates = Segment.list_types_templates()

        for template in templates:
            Segment._survey_template_definition_checker(template)

    def test_add_wrong_template_to_survey(self):
        survey = Segment()
        with self.assertRaises(AssertionError):
            survey.save_questions_template({"name": "It's a dict but not proper structure"})

        with self.assertRaises(ValueError):
            survey.save_questions_template("we must use valid JSON")

    def test_save_template_to_survey(self):
        survey = Segment()
        self.assertEqual(survey.get_survey_type(), "")
        self.assertEqual(survey.questions_template, None)
        self.assertEqual(survey.answer_template, None)
        survey.save_questions_template(self.survey_1)
        self.assertNotEqual(survey.questions_template, "")
        self.assertNotEqual(survey.answer_template, "")
        self.assertTrue(isinstance(survey.questions_template, str))
