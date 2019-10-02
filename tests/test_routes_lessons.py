import datetime
import unittest
import datamodels
from app import app

from .utils import make_authorized_call


class TestLessonsRoutes(unittest.TestCase):
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
    ):
        segment = datamodels.Segment(
            title=title,
            duration_seconds=duration_seconds,
            url=url,
            language="EN",
            order=1,
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

    def test_change_order_data_validation(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(
            title="intro", course=course, order=0
        )  # intro lesson
        l2 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        l3 = self.make_standard_course_lesson(title="lesson 2", course=course, order=2)
        self.session.add(l1)
        self.session.add(l2)
        self.session.add(l3)
        self.session.commit()

        # No data
        response = make_authorized_call(
            url="/course/abc-123/lessons/reorder",
            user=user,
            data={},
            expected_status_code=400,
        )

        self.assertEqual(response.json["message"], "No data")

        # Empty list
        response = make_authorized_call(
            url="/course/abc-123/lessons/reorder",
            user=user,
            data={"items_order": ""},
            expected_status_code=400,
        )

        self.assertEqual(response.json["message"], "Expected ordered list of items")

        # Wong data
        response = make_authorized_call(
            url="/course/abc-123/lessons/reorder",
            user=user,
            data={"items_order": "1,s,0"},
            expected_status_code=400,
        )

        self.assertEqual(response.json["message"], "Wrong data format")

        # Wong number of lessons
        response = make_authorized_call(
            url="/course/abc-123/lessons/reorder",
            user=user,
            data={"items_order": "1,2,3,4,5"},
            expected_status_code=400,
        )

        self.assertEqual(response.json["message"], "Wrong number of items")

    def test_change_order_unauthorized(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)

        make_authorized_call(
            url="/course/abc-123/lessons/reorder",
            user=user,
            data={"items_order": "{},{}".format(1, 2)},
            expected_status_code=404,
        )

    def test_change_order_of_intro_lesson(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(
            title="intro", course=course, order=0
        )  # intro lesson
        l2 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        l3 = self.make_standard_course_lesson(title="lesson 2", course=course, order=2)
        self.session.add(l1)
        self.session.add(l2)
        self.session.add(l3)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/reorder",
            user=user,
            data={"items_order": "{},{}".format(l2.id, l1.id)},
            expected_status_code=400,
        )

        self.assertEqual(response.json["message"], "Wrong number of items")

    def test_change_lessons_order(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(
            title="intro", course=course, order=0
        )  # intro lesson
        l2 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        l3 = self.make_standard_course_lesson(title="lesson 2", course=course, order=2)
        self.session.add(l1)
        self.session.add(l2)
        self.session.add(l3)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/reorder",
            user=user,
            data={"items_order": "{},{}".format(l3.id, l2.id)},
            expected_status_code=200,
        )

        self.assertEqual(response.json["message"], "Order updated")
        self.assertEqual(self.session.query(datamodels.Lesson).get(l3.id).order, 1)
        self.assertEqual(self.session.query(datamodels.Lesson).get(l2.id).order, 2)

    def test_delete_lesson(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(
            title="intro", course=course, order=0
        )  # intro lesson
        l2 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        l3 = self.make_standard_course_lesson(title="lesson 2", course=course, order=2)
        l4 = self.make_standard_course_lesson(title="lesson 3", course=course, order=3)
        self.session.add(l1)
        self.session.add(l2)
        self.session.add(l3)
        self.session.add(l4)
        self.session.commit()

        self.assertEqual(len(course.lessons), 4)

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/delete".format(l3.id),
            user=user,
            data={},
            expected_status_code=200,
        )

        self.assertEqual(len(course.lessons), 3)
        self.assertEqual(response.json["success_url"], "/course/abc-123/edit")
        lessons = datamodels.Lesson.get_ordered_items()
        self.assertEqual(lessons[0].order, 1)
        self.assertEqual(lessons[0].title, "lesson 1")
        self.assertEqual(lessons[1].order, 2)
        self.assertEqual(lessons[1].title, "lesson 3")

    def test_delete_wrong_lesson_id(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)

        response = make_authorized_call(
            url="/course/abc-123/lessons/10000000/delete",
            user=user,
            data={},
            expected_status_code=400,
        )

        self.assertFalse(response.json["success"])

    def test_delete_lesson_not_in_course(self):
        course = self.make_standard_course(guest_access=True)
        course2 = self.make_standard_course(
            guest_access=True, slug="course-2", code="course2", title="course 2"
        )
        self.session.add(course)
        self.session.add(course2)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)

        l1 = self.make_standard_course_lesson(title="intro", course=course2, order=0)
        self.session.add(l1)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/delete".format(l1.id),
            user=user,
            data={},
            expected_status_code=400,
        )

        self.assertFalse(response.json["success"])

    def test_add_lesson(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()

        self.assertEqual(len(course.lessons), 0)

        response = make_authorized_call(
            url="/course/abc-123/lessons/add",
            user=user,
            data={
                "title": "Get out of the building",
                "description": "Don't be afraid of talking to people.",
            },
            expected_status_code=302,
        )

        self.assertEqual(len(course.lessons), 1)

    def test_add_lesson_without_data(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()

        self.assertEqual(len(course.lessons), 0)

        response = make_authorized_call(
            url="/course/abc-123/lessons/add",
            user=user,
            data={"title": "Get out of the building"},
            expected_status_code=302,
        )

        self.assertEqual(len(course.lessons), 0)
