import json
import unittest

import datamodels
from app import app
from datamodels.enums import SurveyTypeEnum, SegmentType
from datamodels.segments import SegmentSurveyResponse
from datamodels.survey_templates import SURVEYS_TEMPLATES
from .utils import ObjectsGenerator

from charts.survey_stats import get_survey_statistics


class TestSurveyStats(ObjectsGenerator, unittest.TestCase):
    number_of_students = 10

    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()
            self.set_basic_course()

            self.l1 = self.make_standard_course_lesson(
                title="lesson 1", course=self.course, order=1
            )
            self.session.add(self.l1)
            self.session.commit()
            self.l1s0 = self.make_segment(self.l1, title="Segment Intro", order=0, slug="segment-intro")
            self.session.add(self.l1s0)
            self.session.commit()

            self.students = []
            for i in range(1, self.number_of_students + 1):
                student = self.makeUser(id=i+1, email="student_{}@fitzroyacademy.com".format(i),
                                        username="student_{}".format(i))
                self.session.add(student)
                self.session.commit()
                self.students.append(student)
                self.course.enroll(student)

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def generate_surveys_responses(self, survey_idx, prefix=""):
        segment = self.make_segment(lesson=self.l1,
                                    seg_type=SegmentType.survey,
                                    survey_type=SurveyTypeEnum.points_scale)
        segment.save_questions_template(SURVEYS_TEMPLATES[survey_idx].copy())
        segment.save()

        answer_template = SURVEYS_TEMPLATES[survey_idx]["answer_template"].copy()

        for i in range(1, self.number_of_students + 1):
            answer_template["chosen_answer"] = "{}{}".format(prefix, i % 3 + 1)
            r = SegmentSurveyResponse(survey=segment,
                                      user=self.students[i - 1],
                                      answers=json.dumps(answer_template)
                                      )
            r.save()

        return segment

    def test_emoji_stats(self):
        segment = self.generate_surveys_responses(survey_idx=1, prefix="q_")
        statistics = get_survey_statistics(segment)
        self.assertEqual(statistics["responses"]["q_1"], 3)
        self.assertEqual(statistics["number_of_responses"], sum(statistics["responses"].values()))
        self.assertEqual(statistics["number_of_students"], self.number_of_students)

    def test_ten_points_stats(self):
        segment = self.generate_surveys_responses(survey_idx=3)
        statistics = get_survey_statistics(segment)
        self.assertEqual(statistics["responses"]["1"], 3)
        self.assertEqual(statistics["number_of_responses"], sum(statistics["responses"].values()))
        self.assertEqual(statistics["number_of_students"], self.number_of_students)
