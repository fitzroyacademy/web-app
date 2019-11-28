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

    def mockSegments(self):
        c = self.make_standard_course()
        self.session.add(c)
        self.session.commit()
        l1 = self.make_standard_course_lesson(
            title="intro", course=c, order=0
        )
        self.session.add(l1)
        self.session.commit()
        s1 = self.make_segment(
            title="The first segment", lesson=l1, order=1, slug="segment-1"
        )
        s2 = self.make_segment(
            title="The second segment", lesson=l1, order=2, slug="segment-2"
        )
        self.session.add(s1)
        self.session.add(s2)
        self.session.commit()

    def test_add_progress_to_empty_session(self):
        s = app.test_client()
        self.mockSegments()

        response = s.post("/event/progress", data={"segment_id": 1, "percent": 33})

        d = json.loads(response.data)
        self.assertEqual(d['segment_id'], '1')
        self.assertEqual(d['progress'], 33)

        with s.session_transaction() as sess:
            self.assertIn("anon_progress", sess)
            progress = json.loads(sess["anon_progress"])
            self.assertEqual(progress["1"], 33)

    def test_update_progress(self):
        s = app.test_client()
        self.mockSegments()

        with s.session_transaction() as sess:
            sess["anon_progress"] = b'{"1": 2}'

        response = s.post("/event/progress", data={"segment_id": 1, "percent": 34})

        d = json.loads(response.data)
        self.assertEqual(d['segment_id'], '1')

        with s.session_transaction() as sess:
            self.assertIn("anon_progress", sess)
            progress = json.loads(sess["anon_progress"])
            self.assertEqual(progress["1"], 34)

    def test_update_progress_less(self):
        s = app.test_client()
        self.mockSegments()

        with s.session_transaction() as sess:
            sess["anon_progress"] = b'{"1": 35}'

        response = s.post("/event/progress", data={"segment_id": 1, "percent": 10})

        d = json.loads(response.data)
        self.assertEqual(d['segment_id'], '1')

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

        self.mockSegments()

        response = make_authorized_call("/event/progress", user=u, data={"segment_id": 1, "percent": 10})

        d = json.loads(response.data)
        self.assertEqual(d['segment_id'], '1')

        s = app.test_client()
        with s.session_transaction() as sess:
            self.assertNotIn("anon_progress", sess)

        d = json.loads(response.data)
        self.assertEqual(d['segment_id'], '1')
        self.assertEqual(d['user_id'], 1)
        self.assertEqual(d['progress'], 10)
