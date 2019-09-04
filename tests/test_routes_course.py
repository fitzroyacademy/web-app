import datetime
import unittest
import datamodels
from app import app


class TestModels(unittest.TestCase):
    standard_course = {
        'course_code': 'ABC123',
        'title': 'Foo Course',
        'slug': 'abc-123'
    }
    standard_course_lesson = {
        'title': 'Lesson',
        'active': True,
        'language': 'EN',
        'slug': 'lesson',
        'order': 1
    }
    standard_course_lesson_segment = {
        'title': 'Segment',
        'duration_seconds': 200,
        'url': 'fitzroyacademy.com',
        'language': 'EN',
        'order': 1
    }

    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

    def tearDown(self):
        datamodels._clear_session_for_tests()

    @staticmethod
    def makeUser(id=1,
                 first_name='Homer',
                 last_name='Simpson',
                 email="homer@simpsons.com",
                 username="homer",
                 password="password",
                 phone_number="555-444-1234",
                 dob=None):
        dob = dob or datetime.datetime.now()
        u = datamodels.User(
            id=id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            phone_number=phone_number,
            dob=dob)
        u.password = 'password'
        return u

    def test_homepage(self):
        s = app.test_client()
        response = s.get('/course/')
        self.assertEqual(response.status_code, 200)

    def test_course_slug(self):
        s = app.test_client()
        response = s.get('/course/no-such-course-slug')
        # If there is no course with given slug then we're redirected to 404
        self.assertEqual(response.status_code, 302)

        # There is course without lessons
        course = datamodels.Course(guest_access=True, **self.standard_course)
        self.session.add(course)

        with self.assertRaises(IndexError):
            response = s.get('/course/abc-123')

        lesson = datamodels.Lesson(
            course=course, **self.standard_course_lesson)
        self.session.add(lesson)

        with self.assertRaises(IndexError):  # Lesson without segment
            response = s.get('/course/abc-123')

        segment = datamodels.Segment(
            lesson=lesson,
            **self.standard_course_lesson_segment,
            _thumbnail='thumbnail_1')
        self.session.add(segment)

        response = s.get('/course/abc-123')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(response.data).find('Foo Course'))

    def test_course_code(self):
        course = datamodels.Course(guest_access=True, **self.standard_course)
        self.session.add(course)
        lesson = datamodels.Lesson(
            course=course, **self.standard_course_lesson)
        self.session.add(lesson)
        segment = datamodels.Segment(
            lesson=lesson,
            **self.standard_course_lesson_segment,
            _thumbnail='thumbnail_1')
        self.session.add(segment)

        s = app.test_client()
        response = s.get('/course/code')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            str(response.data).find('That didn\’t work. Try again?'))

        response = s.post('/course/code', data={'course_code': 'no-such-slug'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            str(response.data).find('That didn\’t work. Try again?'))

        response = s.post('/course/code', data={'course_code': 'ABC123'})
        self.assertEqual(response.status_code, 302)

    def test_set_course_options(self):
        course = datamodels.Course(guest_access=True, **self.standard_course)
        self.session.add(course)
        lesson = datamodels.Lesson(
            course=course, **self.standard_course_lesson)
        self.session.add(lesson)
        segment = datamodels.Segment(
            lesson=lesson,
            **self.standard_course_lesson_segment,
            _thumbnail='thumbnail_1')
        self.session.add(segment)

        s = app.test_client()

        # No permission to set course options
        response = s.post('/course/abc-123/edit/options/paid/on')
        self.assertEqual(response.status_code, 404)

        u = self.makeUser(id=1)
        self.session.add(u)
        course.enroll(u)

        with s.session_transaction() as sess:
            sess['user_id'] = 1

        response = s.post('/course/abc-123/edit/options/paid/on')
        self.assertEqual(response.status_code, 404)

        # user has permission to set course options
        u2 = self.makeUser(
            email='home@teachers.com', id=2, username='the_teacher')
        self.session.add(u2)
        course.add_instructor(u2)

        with s.session_transaction() as sess:
            sess['user_id'] = 2

        self.assertFalse(course.paid)
        response = s.post('/course/abc-123/edit/options/paid/on')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(course.paid)
        response = s.post('/course/abc-123/edit/options/paid/off')
        self.assertTrue(response.json['success'])
        self.assertFalse(course.paid)

        # Wrong option
        response = s.post('/course/abc-123/edit/options/be_or_not_to_be/off')
        self.assertFalse(response.json['success'])

        # Wrong switcher
        response = s.post('/course/abc-123/edit/options/paid/offff')
        self.assertFalse(response.json['success'])

    def test_edit_course(self):
        course = datamodels.Course(guest_access=True, **self.standard_course)
        self.session.add(course)

        user = self.makeUser(
            email='home@teachers.com', id=2, username='the_teacher')
        self.session.add(user)
        course.add_instructor(user)

        s = app.test_client()

        with s.session_transaction() as sess:
            sess['user_id'] = user.id

        data = {'course_name': 'New title',
                'course_target': 'English poetry lovers',
                'course_summary': 'Do not go gentle into that good night',
                }

        response = s.post('/course/abc-123/edit', data=data)

        self.assertEqual(response.status_code, 200)
        course = datamodels.get_course_by_slug('abc-123')
        self.assertEqual(course.title, 'New title')
        self.assertEqual(course.summary_html, 'Do not go gentle into that good night')
        self.assertEqual(course.target_audience, 'English poetry lovers')

