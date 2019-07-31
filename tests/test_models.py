import datamodels
import unittest
import datetime
import string
import random

class TestModels(unittest.TestCase):

    def setUp(self):
        self.session = datamodels.get_session()

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def test_user_creation(self):
        password = ''.join(random.choice([string.ascii_letters + string.digits]) for x in range(16))
        first_name = 'Homer'
        last_name = 'Simpson'
        email = "homer.simpson@fitzroyacademy.com"
        username = "krustyburger80"
        phone_number = "555-444-1234"
        dob = datetime.datetime.now()
        u = datamodels.User(id=1, first_name=first_name, last_name=last_name, 
            email=email, username=username, phone_number=phone_number, dob=dob)
        u.password = password
        self.session.add(u)
        u2 = datamodels.get_user(1)
        self.assertEqual(u2.full_name, 'Homer Simpson')
        self.assertEqual(u2.email, email)
        self.assertTrue(u2.check_password, password)

    def test_user_not_found(self):
        u = datamodels.get_user(1)
        self.assertEqual(u, None)

    def test_course_creation(self):
        c = datamodels.Course(id=1, course_code="ABC123", title="Foo Course")
        self.session.add(c)
        c = datamodels.get_course_by_code('ABC123')
        self.assertEqual(c.title, "Foo Course")

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

