import datetime
import unittest
import datamodels
from app import app

from .utils import make_authorized_call, ObjectsGenerator


class TestUserEnrollment(ObjectsGenerator, unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

        self.user = self.makeUser()
        self.session.add(self.user)
        self.session.commit()

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def test_free_access_no_code_no_login_anonymous_user(self):
        """
        Test a scenario when an anonymous user tries to enroll for a course that is: free of charge, public and login
        is not required. In that case user should be enrolled and redirected to course's lesson.
        """
        course = self.make_standard_course(
            guest_access=True, paid=False, visibility="public"
        )
        l = self.make_standard_course_lesson(course=course)
        self.session.add(course)
        self.session.add(l)
        self.session.commit()

        s = app.test_client()
        response = s.post("/enroll/{}".format(course.slug))

        with s.session_transaction() as sess:
            self.assertEqual(sess["enrollments"], "[{}]".format(course.id))

    def test_free_access_no_code_no_login_legged_in_user(self):
        """
        Test a scenario when a logged in user tries to enroll for a course that is: free of charge, public and login
        is not required. In that case user should be enrolled and redirected to course's lesson.
        """
        course = self.make_standard_course(
            guest_access=True, paid=False, visibility="public"
        )
        l = self.make_standard_course_lesson(course=course)
        self.session.add(course)
        self.session.add(l)
        self.session.commit()

        make_authorized_call(
            url="/enroll/{}".format(course.slug),
            user=self.user,
            expected_status_code=302,
        )

        self.assertTrue(course.is_student(self.user.id))

    def test_free_access_code_no_login_no_code_provided(self):
        """
        Test a scenario when an anonymous or a logged in user tries to enroll for a course that is: free of charge, requires code
        but login is not required. User provide wrong course code.
        In that case user should be redirected to a course page.
        """
        course = self.make_standard_course(
            guest_access=True, paid=False, visibility="code"
        )
        l = self.make_standard_course_lesson(course=course)
        self.session.add(course)
        self.session.add(l)
        self.session.commit()

        # Anonymous user
        s = app.test_client()
        s.post("/enroll/{}".format(course.slug))

        with s.session_transaction() as sess:
            self.assertNotIn("enrollments", sess)

        # Logged in user
        make_authorized_call(
            url="/enroll/{}".format(course.slug),
            user=self.user,
            expected_status_code=302,
        )

        self.assertFalse(course.is_student(self.user.id))

    def test_free_access_code_no_login(self):
        """
        Test a scenario when an anonymous or a logged in user tries to enroll for a course that is: free of charge, requires code
        but login is not required. User provide correct course code.
        In that case user should be enrolled and redirected to the first course lesson.
        """

        course = self.make_standard_course(
            guest_access=True, paid=False, visibility="code"
        )
        l = self.make_standard_course_lesson(course=course)
        self.session.add(course)
        self.session.add(l)
        self.session.commit()

        data = {"course_code": course.course_code}

        # Anonymous user
        s = app.test_client()
        s.post("/enroll/{}".format(course.slug), data=data)

        with s.session_transaction() as sess:
            self.assertEqual(sess["enrollments"], "[{}]".format(course.id))

        # Logged in user
        make_authorized_call(
            url="/enroll/{}".format(course.slug),
            user=self.user,
            data=data,
            expected_status_code=302,
        )

        self.assertTrue(course.is_student(self.user.id))

    def test_free_access_public_login_required(self):
        course = self.make_standard_course(
            guest_access=False, paid=False, visibility="public"
        )
        l = self.make_standard_course_lesson(course=course)
        self.session.add(course)
        self.session.add(l)
        self.session.commit()

        # Anonymous user
        s = app.test_client()
        s.post("/enroll/{}".format(course.slug))

        with s.session_transaction() as sess:
            self.assertNotIn("enrollments", sess)

        # Logged in user
        make_authorized_call(
            url="/enroll/{}".format(course.slug),
            user=self.user,
            expected_status_code=302,
        )

        self.assertTrue(course.is_student(self.user.id))
