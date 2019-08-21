import datamodels
import unittest
import datetime
import string
import random
from app import app


class TestModels(unittest.TestCase):

    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def makeUser(self, id=1, first_name='Homer', last_name='Simpson',
                 email="homer@simpsons.com", username="homer",
                 password="password", phone_number="555-444-1234",
                 dob=None):
        dob = dob or datetime.datetime.now()
        u = datamodels.User(id=1, first_name=first_name, last_name=last_name, 
            email=email, username=username, phone_number=phone_number, dob=dob)
        u.password = 'password'
        return u

    def test_user_creation(self):
        u = self.makeUser(
            id=1,
            first_name="Marge", last_name="Simpson",
            email="marge@simpsons.com",
            password="password"
        )
        self.session.add(u)
        u2 = datamodels.get_user(1)
        self.assertEqual(u2.full_name, 'Marge Simpson')
        self.assertEqual(u2.email, 'marge@simpsons.com')
        self.assertTrue(u2.check_password, 'password')

    def test_student_enrollment(self):
        u = self.makeUser(id=1)
        self.session.add(u)
        c = datamodels.Course(id=1, course_code="ABC123", title="Foo Course", slug="abc-123")
        self.session.add(c)
        c.enroll(u)
        u2 = datamodels.get_user(1)
        self.assertEqual(len(u2.courses), 1)
        self.assertEqual(u2.courses[0].id, 1)
        self.assertEqual(
            u2.course_enrollments[0].access_level,
            datamodels.COURSE_ACCESS_STUDENT
        )

    def test_user_not_found(self):
        u = datamodels.get_user(1)
        self.assertEqual(u, None)

    def test_course_creation(self):
        c = datamodels.Course(id=1, course_code="ABC123", title="Foo Course", slug="abc-123")
        self.session.add(c)
        c = datamodels.get_course_by_code('ABC123')
        c2 = datamodels.get_course_by_slug("abc-123")
        self.assertEqual(c.title, "Foo Course")
        self.assertEqual(c, c2)

    def test_public_course_creation(self):
        c = datamodels.Course(id=2, course_code="DEF456", title="Bar Course", guest_access=True)
        self.session.add(c)
        c_results = datamodels.get_public_courses()
        for result in c_results:
            if result.course_code=='DEF456':
                c = result
        self.assertEqual(c.title, 'Bar Course')

    def test_course_not_found(self):
        u = datamodels.get_course_by_code('ABC123')
        self.assertEqual(u, None)

    def test_lesson_creation(self):
        l = datamodels.Lesson(id=1,title="Lesson", active=True, language="EN", slug="lesson", order=1)
        self.session.add(l)
        l = datamodels.get_lesson(1)
        self.assertEqual(l.title, "Lesson")

    def test_segment_creation(self):
        s = datamodels.Segment(id=1, title="Segment", duration_seconds=200, url="fitzroyacademy.com", language="EN", order=1)
        self.session.add(s)
        s = datamodels.get_segment(1)
        self.assertEqual(s.title, "Segment")
