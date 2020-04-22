import datetime
import unittest
import datamodels
from app import app

from .utils import make_authorized_call


class TestCourseRoutes(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

    def tearDown(self):
        datamodels._clear_session_for_tests()

    @staticmethod
    def make_standard_course(
        code="ABC123",
        guest_access=False,
        title="Foo Course",
        slug="abc-123",
        draft=False,
    ):
        course = datamodels.Course(
            course_code=code,
            title=title,
            slug=slug,
            guest_access=guest_access,
            draft=draft,
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

    def test_homepage(self):
        s = app.test_client()
        response = s.get("/course/")
        self.assertEqual(response.status_code, 200)

    def test_course_slug(self):
        s = app.test_client()
        response = s.get("/course/no-such-course-slug")
        # If there is no course with given slug then we're redirected to 404
        self.assertEqual(response.status_code, 302)

        # There is course without lessons
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        lesson = self.make_standard_course_lesson(course=course)
        self.session.add(lesson)

        segment = self.make_segment(lesson, "thumbnail_1")
        self.session.add(segment)

        response = s.get("/course/abc-123")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(response.data).find("Foo Course"))

    def test_course_code(self):
        course = self.make_standard_course()
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course)
        self.session.add(lesson)
        segment = self.make_segment(lesson=lesson, thumbnail="thumbnail_1")
        self.session.add(segment)

        s = app.test_client()
        response = s.get("/course/code")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(response.data).find("That didn\’t work. Try again?"))

        response = s.post("/course/code", data={"course_code": "no-such-slug"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(response.data).find("That didn\’t work. Try again?"))

        response = s.post("/course/code", data={"course_code": "ABC123"})
        self.assertEqual(response.status_code, 302)

    def test_set_course_options(self):
        course = self.make_standard_course()
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course)
        self.session.add(lesson)
        segment = self.make_segment(lesson=lesson, thumbnail="thumbnail_1")
        self.session.add(segment)
        self.session.add(course)
        self.session.commit()
        
        s = app.test_client()

        # No permission to set course options
        response = s.post("/course/abc-123/edit/options/paid/on")
        self.assertEqual(response.status_code, 401)

        u = self.makeUser(id=1)
        self.session.add(u)
        course.enroll(u)

        with s.session_transaction() as sess:
            sess["user_id"] = 1

        response = s.post("/course/abc-123/edit/options/paid/on")
        self.assertEqual(response.status_code, 404)

        # user has permission to set course options
        u2 = self.makeUser(email="home@teachers.com", id=2, username="the_teacher")
        self.session.add(u2)
        course.add_instructor(u2)

        with s.session_transaction() as sess:
            sess["user_id"] = 2

        self.assertFalse(course.paid)
        response = s.post("/course/abc-123/edit/options/paid/on")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(course.paid)
        response = s.post("/course/abc-123/edit/options/paid/off")
        self.assertTrue(response.json["success"])
        self.assertFalse(course.paid)

        # Wrong option
        response = s.post("/course/abc-123/edit/options/be_or_not_to_be/off")
        self.assertFalse(response.json["success"])

        # Wrong switcher / by default option is set to false
        response = s.post("/course/abc-123/edit/options/paid/offff")
        self.assertTrue(response.json["success"])
        self.assertFalse(course.paid)

    def test_set_course_visibility(self):
        course = self.make_standard_course()
        course.visibility = "public"
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course)
        self.session.add(lesson)
        segment = self.make_segment(lesson=lesson, thumbnail="thumbnail_1")
        self.session.add(segment)
        u1 = self.makeUser(email="home@teachers.com", id=2, username="the_teacher")
        self.session.add(u1)
        self.session.commit()

        s = app.test_client()

        # user has permission to set course options
        course.add_instructor(u1)

        with s.session_transaction() as sess:
            sess["user_id"] = 2

        # wrong visibility
        self.assertEqual(course.visibility, "public")
        response = s.post("/course/abc-123/edit/options/visibility/thereisnosuch")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(course.visibility, "public")

        # wrong visibility
        response = s.post("/course/abc-123/edit/options/visibility/institute")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(course.visibility, "institute")

        # wrong visibility
        response = s.post("/course/abc-123/edit/options/visibility/code")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(course.visibility, "code")

        # wrong visibility
        response = s.post("/course/abc-123/edit/options/visibility/public")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(course.visibility, "public")

    def test_edit_course(self):
        course = self.make_standard_course(guest_access=True)
        course2 = self.make_standard_course(
            slug="some_other_course", title="Some other course", code="123456"
        )
        self.session.add(course)
        self.session.add(course2)

        user = self.makeUser(email="home@teachers.com", id=2, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)

        s = app.test_client()

        with s.session_transaction() as sess:
            sess["user_id"] = user.id

        data = {
            "course_name": "New title",
            "who_its_for": "English poetry lovers",
            "course_summary": "Do not go gentle into that good night",
        }

        response = s.post("/course/abc-123/edit", data=data)

        self.assertEqual(response.status_code, 200)
        course = datamodels.Course.find_by_slug("abc-123")
        self.assertEqual(course.title, "New title")
        self.assertEqual(course.summary_html, "Do not go gentle into that good night")
        self.assertEqual(course.target_audience, "English poetry lovers")

        # change slug to a new one
        make_authorized_call(
            url="/course/abc-123/edit/slug",
            user=user,
            data={"slug": "fancy_slug"},
            expected_status_code=200,
        )
        course = datamodels.Course.find_by_slug("fancy_slug")
        self.assertEqual(course.title, "New title")

        # change slug to an existing one
        make_authorized_call(
            url="/course/fancy_slug/edit/slug",
            user=user,
            data={"slug": "some_other_course"},
            expected_status_code=400,
        )
        course = datamodels.Course.find_by_slug("fancy_slug")
        self.assertIsNotNone(course)

        # change code to a new one
        make_authorized_call(
            url="/course/fancy_slug/edit",
            user=user,
            data={"course_code": "AABBCC"},
            expected_status_code=200,
        )
        course = datamodels.Course.find_by_code("AABBCC")
        self.assertEqual(course.title, "New title")

        # change code to an existing one
        make_authorized_call(
            url="/course/fancy_slug/edit",
            user=user,
            data={"course_code": "123456"},
            expected_status_code=400,
        )
        response = s.post("/course/fancy_slug/edit", data=data)
        course = datamodels.Course.find_by_code("AABBCC")
        self.assertIsNotNone(course)

        # change course year
        make_authorized_call(
            url="/course/fancy_slug/edit",
            user=user,
            data={"year": 2020},
            expected_status_code=200,
        )
        course = datamodels.Course.find_by_code("AABBCC")
        self.assertEqual(course.year.year, 2020)

        # wrong year
        make_authorized_call(
            url="/course/fancy_slug/edit",
            user=user,
            data={"year": "123aaa"},
            expected_status_code=400,
        )

        # wrong amount
        make_authorized_call(
            url="/course/fancy_slug/edit",
            user=user,
            data={"amount": "123aaa"},
            expected_status_code=400,
        )

        # proper amount
        self.assertEqual(course.amount, 0)
        make_authorized_call(
            url="/course/fancy_slug/edit",
            user=user,
            data={"amount": "123.12"},
            expected_status_code=200,
        )

        self.assertEqual(course.amount, 12312)

    def test_remove_teacher(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        user1 = self.makeUser(email="home1@teachers.com", id=2, username="the_teacher1")
        user2 = self.makeUser(email="home2@teachers.com", id=3, username="the_teacher3")
        self.session.add(user2)
        self.session.add(user1)
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        course.add_instructor(user1)

        self.assertEqual(len(course.instructors), 2)

        # Teacher do not teaches this course
        make_authorized_call(
            url="/course/abc-123/edit/remove/teacher/{}".format(user.id),
            user=user2,
            expected_status_code=404,
        )

        # Teacher try's to remove herself
        make_authorized_call(
            url="/course/abc-123/edit/remove/teacher/{}".format(user.id),
            user=user,
            expected_status_code=400,
        )

        # Teacher try\s to remove nonexisting user
        make_authorized_call(
            url="/course/abc-123/edit/remove/teacher/999",
            user=user,
            expected_status_code=400,
        )

        # Finally remove teacher
        make_authorized_call(
            url="/course/abc-123/edit/remove/teacher/{}".format(user1.id),
            user=user,
            expected_status_code=200,
        )
        self.assertEqual(len(course.instructors), 1)

    def test_add_teacher(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)

        user1 = self.makeUser(email="home1@teachers.com", id=2, username="the_teacher1")
        self.session.add(user1)

        self.session.commit()

        # No such email
        make_authorized_call(
            url="/course/abc-123/edit/add/teacher",
            user=user,
            data={"teacher_email": "m@m.com"},
            expected_status_code=400,
        )

        # Add new teacher
        self.assertEqual(len(course.instructors), 1)
        make_authorized_call(
            url="/course/abc-123/edit/add/teacher",
            user=user,
            data={"teacher_email": "home1@teachers.com"},
            expected_status_code=200,
        )

        self.assertEqual(len(course.instructors), 2)
