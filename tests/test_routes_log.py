import json
import unittest
import datamodels
from app import app

from .utils import make_authorized_call, ObjectsGenerator


class TestCourseRoutes(ObjectsGenerator, unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

    def tearDown(self):
        datamodels._clear_session_for_tests()


    def test_add_progress_to_empty_session(self):
        s = app.test_client()

        response = s.post("/event/progress", data={"segment_id": 1, "percent": 33})

        self.assertEqual(response.data, b'{"1": 33}')

        with s.session_transaction() as sess:
            self.assertIn("anon_progress", sess)
            progress = json.loads(sess["anon_progress"])
            self.assertEqual(progress["1"], 33)

    def test_update_progress(self):
        s = app.test_client()

        with s.session_transaction() as sess:
            sess["anon_progress"] = b'{"1": 2}'

        response = s.post("/event/progress", data={"segment_id": 1, "percent": 34})

        self.assertEqual(response.data, b'{"1": 34}')

        with s.session_transaction() as sess:
            self.assertIn("anon_progress", sess)
            progress = json.loads(sess["anon_progress"])
            self.assertEqual(progress["1"], 34)

    def test_update_progress_less(self):
        s = app.test_client()

        with s.session_transaction() as sess:
            sess["anon_progress"] = b'{"1": 35}'

        response = s.post("/event/progress", data={"segment_id": 1, "percent": 10})

        self.assertEqual(response.data, b'{"1": 35}')

        with s.session_transaction() as sess:
            self.assertIn("anon_progress", sess)
            progress = json.loads(sess["anon_progress"])
            self.assertEqual(progress["1"], 35)

    def test_add_event_foobar(self):
        s = app.test_client()

        response = s.post("/event/foobar", data={"segment_id": 1, "percent": 10})

        self.assertEqual(response.data, b"foobar")

    def test_add_event_with_logged_user(self):
        u = self.makeUser()
        self.session.add(u)
        self.session.commit()

        course = self.make_standard_course(guest_access=True)
        self.session.add(course)
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        s1 = self.make_segment(l1, title="Segment Intro", order=0, slug="segment-intro")
        self.session.add(s1)
        self.session.commit()

        response = make_authorized_call("/event/progress", user=u, data={"segment_id": s1.id, "percent": 10})

        s = app.test_client()
        with s.session_transaction() as sess:
            self.assertNotIn("anon_progress", sess)

        self.assertEqual(b'{"id": 1, "progress": 10, "segment_id": 1, "user_id": 1}', response.data)
