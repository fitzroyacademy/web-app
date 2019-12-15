import unittest
import datamodels
from app import app

from .utils import ObjectsGenerator


class TestUserProgress(ObjectsGenerator, unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

            self.course = self.make_standard_course(guest_access=True)
            self.session.add(self.course)

            self.l0 = self.make_standard_course_lesson(
                title="Intro lesson", course=self.course, order=0
            )
            self.l1 = self.make_standard_course_lesson(
                title="lesson 1", course=self.course, order=1
            )
            self.l2 = self.make_standard_course_lesson(
                title="lesson 2", course=self.course, order=1
            )
            self.session.add(self.l0)
            self.session.add(self.l1)
            self.session.add(self.l2)

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def test_previous_segment(self):
        self.l0s0 = self.make_segment(
            self.l0, title="Intro segment", order=0, slug="intro-segment"
        )
        self.l0s1 = self.make_segment(
            self.l0, title="Segment l0l1", order=1, slug="segment-1"
        )
        self.l1s1 = self.make_segment(
            self.l1, title="Intro segment l1", order=0, slug="intro-segment-l1"
        )
        self.l1s2 = self.make_segment(
            self.l1, title="Segment l1s1", order=1, slug="segment-1"
        )
        self.session.add(self.l0s0)
        self.session.add(self.l0s1)
        self.session.add(self.l1s1)
        self.session.add(self.l1s2)
        self.session.commit()

        self.assertEqual(self.l1s2.previous.id, self.l1s1.id)
        self.assertEqual(self.l1s1.previous.id, self.l0s1.id)
        self.assertEqual(self.l0s1.previous.id, self.l0s0.id)
        self.assertIsNone(self.l0s0.previous)

    def test_next_segment(self):
        self.l0s0 = self.make_segment(
            self.l0, title="Intro segment", order=0, slug="intro-segment"
        )
        self.l0s1 = self.make_segment(
            self.l0, title="Segment l0l1", order=1, slug="segment-1"
        )
        self.l1s1 = self.make_segment(
            self.l1, title="Intro segment l1", order=0, slug="intro-segment-l1"
        )
        self.l1s2 = self.make_segment(
            self.l1, title="Segment l1s1", order=1, slug="segment-1"
        )
        self.session.add(self.l0s0)
        self.session.add(self.l0s1)
        self.session.add(self.l1s1)
        self.session.add(self.l1s2)
        self.session.commit()

        self.assertEqual(self.l0s0.next.id, self.l0s1.id)
        self.assertEqual(self.l0s1.next.id, self.l1s1.id)
        self.assertEqual(self.l1s1.next.id, self.l1s2.id)
        self.assertIsNone(self.l1s2.next)
