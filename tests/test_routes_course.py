import unittest

import datamodels
from app import app


class TestModels(unittest.TestCase):
    standard_course = {'course_code': 'ABC123', 'title': 'Foo Course', 'slug': 'abc-123'}
    standard_course_lesson = {'title': 'Lesson', 'active': True, 'language': 'EN', 'slug': 'lesson', 'order': 1}
    standard_course_lesson_segment = {'title': 'Segment',
                                      'duration_seconds': 200,
                                      'url': 'fitzroyacademy.com',
                                      'language': 'EN',
                                      'order': 1}

    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

    def tearDown(self):
        datamodels._clear_session_for_tests()

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

        lesson = datamodels.Lesson(course=course, **self.standard_course_lesson)
        self.session.add(lesson)

        with self.assertRaises(IndexError):  # Lesson without segment
            response = s.get('/course/abc-123')

        segment = datamodels.Segment(lesson=lesson, **self.standard_course_lesson_segment, _thumbnail='thumbnail_1')
        self.session.add(segment)

        response = s.get('/course/abc-123')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(response.data).find('Foo Course'))

    def test_course_code(self):
        course = datamodels.Course(guest_access=True, **self.standard_course)
        self.session.add(course)
        lesson = datamodels.Lesson(course=course, **self.standard_course_lesson)
        self.session.add(lesson)
        segment = datamodels.Segment(lesson=lesson, **self.standard_course_lesson_segment, _thumbnail='thumbnail_1')
        self.session.add(segment)

        s = app.test_client()
        response = s.get('/course/code')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(response.data).find('That didn\’t work. Try again?'))

        response = s.post('/course/code', data={'course_code': 'no-such-slug'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(response.data).find('That didn\’t work. Try again?'))

        response = s.post('/course/code', data={'course_code': 'ABC123'})
        self.assertEqual(response.status_code, 302)
