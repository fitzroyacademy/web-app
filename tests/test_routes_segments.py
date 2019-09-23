import datetime
import unittest
import datamodels
from app import app

from .utils import make_authorized_call


class TestSegmentsRoutes(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

    def tearDown(self):
        datamodels._clear_session_for_tests()

    @staticmethod
    def make_standard_course(
        code="ABC123", guest_access=False, title="Foo Course", slug="abc-123"
    ):
        course = datamodels.Course(
            course_code=code, title=title, slug=slug, guest_access=guest_access
        )
        return course

    @staticmethod
    def make_standard_course_lesson(
        course, title="Lesson", active=True, language="EN", slug="lesson", order=1
    ):
        lesson = datamodels.Lesson(
            course=course,
            title=title,
            active=active,
            language=language,
            slug=slug,
            order=order,
        )
        return lesson

    @staticmethod
    def make_segment(
        lesson,
        thumbnail="thumbnail_1",
        title="Segment",
        duration_seconds=200,
        url="fitzroyacademy.com",
        order=0,
    ):
        segment = datamodels.Segment(
            title=title,
            duration_seconds=duration_seconds,
            url=url,
            language="EN",
            order=order,
            _thumbnail=thumbnail,
            lesson=lesson,
        )
        return segment

    @staticmethod
    def makeUser(
        id=1,
        first_name="Homer",
        last_name="Simpson",
        email="homer@simpsons.com",
        username="homer",
        password="password",
        phone_number="555-444-1234",
        dob=None,
    ):
        dob = dob or datetime.datetime.now()
        u = datamodels.User(
            id=id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            phone_number=phone_number,
            dob=dob,
        )
        u.password = password
        return u

    def test_change_order_of_intro_segment(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        s1 = self.make_segment(l1, title="Segment Intro", order=0)
        s2 = self.make_segment(l1, title="Segment 1", order=1)
        s3 = self.make_segment(l1, title="Segment 2", order=2)
        self.session.add(s1)
        self.session.add(s2)
        self.session.add(s3)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/reorder".format(l1.id),
            user=user,
            data={"items_order": "{},{}".format(s2.id, s1.id)},
            expected_status_code=400,
        )

        self.assertEqual(response.json["message"], "Wrong number of items")

    def test_reorder_segments_lesson_not_in_course(self):
        course = self.make_standard_course(guest_access=True)
        course2 = self.make_standard_course(
            guest_access=True, slug="course-2", code="course2", title="course 2"
        )
        self.session.add(course)
        self.session.add(course2)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(title="lesson 1", course=course2, order=1)
        self.session.add(l1)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/reorder".format(l1.id),
            user=user,
            data={"items_order": "1,2"},
            expected_status_code=400,
        )

        self.assertEqual(response.json["message"], "Course do not match lesson")

    def test_change_segment_order(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        s1 = self.make_segment(l1, title="Segment Intro", order=0)
        s2 = self.make_segment(l1, title="Segment 1", order=1)
        s3 = self.make_segment(l1, title="Segment 2", order=2)
        self.session.add(s1)
        self.session.add(s2)
        self.session.add(s3)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/reorder".format(l1.id),
            user=user,
            data={"items_order": "{},{}".format(s3.id, s2.id)},
            expected_status_code=200,
        )

        self.assertEqual(response.json["message"], "Order updated")
        self.assertEqual(self.session.query(datamodels.Segment).get(s3.id).order, 1)
        self.assertEqual(self.session.query(datamodels.Segment).get(s2.id).order, 2)

    def test_delete_segment(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        s1 = self.make_segment(l1, title="Segment Intro", order=0)
        s2 = self.make_segment(l1, title="Segment 1", order=1)
        s3 = self.make_segment(l1, title="Segment 2", order=2)
        self.session.add(s1)
        self.session.add(s2)
        self.session.add(s3)
        self.session.commit()

        self.assertEqual(len(l1.segments), 3)

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/{}/delete".format(l1.id, s3.id),
            user=user,
            data={},
            expected_status_code=200,
        )

        self.assertEqual(len(l1.segments), 2)
        self.assertEqual(
            response.json["success_url"],
            "/course/abc-123/lessons/{}/edit".format(l1.id),
        )
        lessons = datamodels.Segment.get_ordered_items()
        self.assertEqual(lessons[0].order, 1)
        self.assertEqual(lessons[0].title, "Segment 1")

    def test_delete_wrong_segment_id(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/1000000000/delete".format(l1.id),
            user=user,
            data={},
            expected_status_code=400,
        )

        self.assertFalse(response.json["success"])

    def test_delete_segment_not_in_course(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(title="intro", course=course, order=0)
        l2 = self.make_standard_course_lesson(
            title="other lesson", course=course, order=1
        )
        self.session.add(l1)
        self.session.add(l2)
        s1 = self.make_segment(l1, title="Segment Intro", order=0)
        s2 = self.make_segment(l2, title="Segment Intro 2", order=0)
        self.session.add(s1)
        self.session.add(s2)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/{}/delete".format(l1.id, s2.id),
            user=user,
            data={},
            expected_status_code=400,
        )

        self.assertFalse(response.json["success"])
