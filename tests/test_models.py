import datamodels
import unittest

class TestModels(unittest.TestCase):

    def setUp(self):
        self.session = datamodels.get_session()

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def test_user_creation(self):
        u = datamodels.User(id=1, first_name="Homer", last_name="Simpson")
        self.session.add(u)
        u2 = datamodels.get_user(1)
        self.assertEqual(u2.full_name, 'Homer Simpson')

    def test_user_not_found(self):
        u = datamodels.get_user(1)
        self.assertEqual(u, None)

    def test_course_creation(self):
        c = datamodels.Course(id=1, course_code="ABC123", title="Foo Course")
        self.session.add(c)
        c = datamodels.get_course_by_code('ABC123')
        self.assertEqual(c.title, "Foo Course")

    def test_course_not_found(self):
        u = datamodels.get_course_by_code('ABC123')
        self.assertEqual(u, None)