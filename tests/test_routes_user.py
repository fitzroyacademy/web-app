import json
import unittest
import datamodels
from app import app

from routes.utils import get_session_data, set_session_data

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

    def test_user_create(self):
        s = app.test_client()

        self.assertEqual(datamodels.User.objects().count(), 1)
        s.post(
            "/register",
            data={
                "first_name": "Tom",
                "last_name": "Riddle",
                "username": "Tom Riddle",
                "email": "lord_voldemort@hogwart.com",
                "password": "password",
            },
            follow_redirects=True,
        )

        self.assertEqual(datamodels.User.objects().count(), 2)
        new_user = datamodels.User.find_by_email("lord_voldemort@hogwart.com")
        self.assertEqual(new_user.username, "tom-riddle")

        with s.session_transaction() as sess:
            self.assertEqual(sess["user_id"], new_user.id)

    def test_user_create_same_username(self):
        s = app.test_client()

        self.assertEqual(datamodels.User.objects().count(), 1)
        s.post(
            "/register",
            data={
                "first_name": "Tom",
                "last_name": "Riddle",
                "username": "homer",
                "email": "lord_voldemort@hogwart.com",
                "password": "password",
            },
            follow_redirects=True,
        )

        self.assertEqual(datamodels.User.objects().count(), 2)
        new_user = datamodels.User.find_by_email("lord_voldemort@hogwart.com")
        self.assertNotEqual(new_user.username, "homer")
        self.assertTrue(
            new_user.username.startswith("homer")
        )  # username starts with homer but contains part of UUID4

    def test_user_login_success(self):
        s = app.test_client()

        s.post("/login", data={"email": self.user.email, "password": "password"})

        with s.session_transaction() as sess:
            self.assertEqual(sess["user_id"], self.user.id)

    def test_user_login_failed(self):
        s = app.test_client()

        # No such user
        response = s.post(
            "/login",
            data={"email": "no_such_user@userdatabase.com", "password": "password"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue("Bad username or password, try again" in str(response.data))

        with s.session_transaction() as sess:
            with self.assertRaises(KeyError):
                id = sess["user_id"]

        # Wrong password
        response = s.post(
            "/login",
            data={"email": self.user.email, "password": "super_wrong_password"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue("Bad username or password, try again" in str(response.data))

        with s.session_transaction() as sess:
            with self.assertRaises(KeyError):
                id = sess["user_id"]

    def test_user_login_no_credentials(self):
        s = app.test_client()

        # no password provided
        response = s.post(
            "/login",
            data={"email": "no_such_user@userdatabase.com", "password": ""},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

        with s.session_transaction() as sess:
            with self.assertRaises(KeyError):
                id = sess["user_id"]

        # no email provided
        response = s.post(
            "/login", data={"email": "", "password": "asdfas"}, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        with s.session_transaction() as sess:
            with self.assertRaises(KeyError):
                id = sess["user_id"]

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


class TestUserSettings(ObjectsGenerator, unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

        self.user = self.makeUser()
        self.session.add(self.user)
        self.session.commit()

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def test_set_setting_anonymous(self):
        s = app.test_client()

        response = s.post("/user/settings", data={"key": "hardware", "value": "macbook"})

        d = json.loads(response.data)
        self.assertEqual(d["key"], "hardware")
        self.assertEqual(d["value"], "macbook")

        with s.session_transaction() as sess:
            self.assertIn("custom_settings", sess)
            custom_settings = get_session_data(sess, "custom_settings")
            self.assertEqual(custom_settings["hardware"], "macbook")

    def test_set_setting_logged_in(self):
        response = make_authorized_call("/user/settings", self.user,
                                        data={"key": "hardware", "value": "macbook"})

        self.assertEqual(response.json["key"], "hardware")
        self.assertEqual(response.json["value"], "macbook")

        custom_settings = self.user.get_custom_settings()
        self.assertEqual(custom_settings['hardware'], "macbook")

    def test_set_settings_wrong_data(self):
        make_authorized_call("/user/settings", self.user,
                             data={"key": "", "value": "macbook"},
                             expected_status_code=400)

        make_authorized_call("/user/settings", self.user,
                             data={"key": "hardware", "value": ""},
                             expected_status_code=400)

    def test_get_settings_logged_in(self):
        datamodels.CustomSetting.set_setting("foo", "bar", self.user)
        datamodels.CustomSetting.set_setting("oof", "rab", self.user)

        response = make_authorized_call("/user/settings", self.user,
                                        expected_status_code=200,
                                        method="GET"
                                        )

        self.assertEqual(response.json["foo"], "bar")
        self.assertEqual(response.json["oof"], "rab")

    def test_get_settings_anonymous(self):
        s = app.test_client()
        with s.session_transaction() as sess:
            set_session_data(sess, "custom_settings", {"foo": "bar", "oof": "rab"})

        response = s.get("/user/settings")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["foo"], "bar")
        self.assertEqual(response.json["oof"], "rab")
