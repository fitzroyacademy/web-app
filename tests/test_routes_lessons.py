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

    def test_add_teacher_without_permission(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/123456789/teacher/add",
            user=user,
            data={"teacher_email": "home@teachers.com"},
            expected_status_code=404,
        )

    def test_wrong_teacher_email(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.teachers), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/teacher/add".format(l1.id),
            user=user,
            data={"teacher_email": "wrong_email_address@teachers.com"},
            expected_status_code=400,
        )
        self.assertFalse(response.json["success"])
        self.assertEqual(response.json["message"], "Can't find that email sorry!")

    def test_add_teacher_to_lesson(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.teachers), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/teacher/add".format(l1.id),
            user=user,
            data={"teacher_email": "home@teachers.com"},
            expected_status_code=200,
        )
        self.assertEqual(len(l1.teachers), 1)

    def test_teacher_already_added(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()
        enrolment = datamodels.CourseEnrollment.find_by_course_and_student(
            course.id, user.id
        )
        l1.teachers.append(enrolment)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.teachers), 1)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/teacher/add".format(l1.id),
            user=user,
            data={"teacher_email": "home@teachers.com"},
            expected_status_code=400,
        )
        self.assertEqual(len(l1.teachers), 1)
        self.assertFalse(response.json["success"])
        self.assertEqual(response.json["message"], "Teacher already added")

    def test_add_user_as_a_teacher(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        user2 = self.makeUser(email="jess@teachers.com", id=2, username="jess_user")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        course.add_user(user2)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.teachers), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/teacher/add".format(l1.id),
            user=user,
            data={"teacher_email": "jess@teachers.com"},
            expected_status_code=400,
        )
        self.assertEqual(len(l1.teachers), 0)
        self.assertFalse(response.json["success"])
        self.assertEqual(response.json["message"], "User must be a teacher")

    def test_remove_teacher(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()
        enrolment = datamodels.CourseEnrollment.find_by_course_and_student(
            course.id, user.id
        )
        l1.teachers.append(enrolment)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.teachers), 1)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/teacher/{}/delete".format(l1.id, user.id),
            user=user,
            expected_status_code=200,
        )
        self.assertEqual(len(l1.teachers), 0)

    def test_remove_teacher_no_such_user(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/teacher/{}/delete".format(l1.id, 123),
            user=user,
            expected_status_code=400,
        )
        self.assertEqual(response.json["message"], "No such teacher")

    def test_add_question(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.questions), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/qa/add".format(l1.id, 123),
            user=user,
            data={"question": "Be or not to be", "answer": "Depends on your believes"},
            expected_status_code=200,
        )
        self.assertEqual(len(l1.questions), 1)
        self.assertEqual(response.json["message"], "Question saved")
        self.assertEqual(l1.questions[0].order, 1)
        self.assertEqual(l1.questions[0].answer, "Depends on your believes")
        self.assertEqual(l1.questions[0].question, "Be or not to be")

    def test_add_question_wrong_data(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.questions), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/qa/add".format(l1.id, 123),
            user=user,
            data={"question": "", "answer": "Depends on your believes"},
            expected_status_code=400,
        )
        self.assertEqual(len(l1.questions), 0)
        self.assertEqual(response.json["message"], "Error saving questions")

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/qa/add".format(l1.id),
            user=user,
            data={"question": "Be or not to be", "answer": ""},
            expected_status_code=400,
        )
        self.assertEqual(len(l1.questions), 0)
        self.assertEqual(response.json["message"], "Error saving questions")

    def test_edit_question(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()
        question = datamodels.LessonQA(
            lesson=l1, question="Why?", answer="Because you can!"
        )
        l1.questions.append(question)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.questions), 1)
        self.assertEqual(l1.questions[0].question, "Why?")
        make_authorized_call(
            url="/course/abc-123/lessons/{}/qa/{}/edit".format(l1.id, question.id),
            user=user,
            data={"question": "Be or not to be", "answer": "Because you can!"},
            expected_status_code=200,
        )
        self.assertEqual(len(l1.questions), 1)
        self.assertEqual(l1.questions[0].question, "Be or not to be")
        self.assertEqual(l1.questions[0].answer, "Because you can!")

    def test_edit_question_from_different_lesson(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        l2 = self.make_standard_course_lesson(title="lesson 2", course=course, order=2)
        self.session.add(l1)
        self.session.add(l2)
        self.session.commit()
        question = datamodels.LessonQA(
            lesson=l1, question="Why?", answer="Because you can!"
        )
        l1.questions.append(question)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l2.questions), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/qa/{}/edit".format(l2.id, question.id),
            user=user,
            data={"question": "Be or not to be", "answer": "Because you can!"},
            expected_status_code=400,
        )
        self.assertEqual(len(l2.questions), 0)
        self.assertEqual(response.json["message"], "Wrong question or lesson")

    def test_remove_question(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()
        q1 = datamodels.LessonQA(
            lesson=l1, question="Why 1?", answer="Because you can do 1!", order=1
        )
        q2 = datamodels.LessonQA(
            lesson=l1, question="Why 2?", answer="Because you can do 2!", order=2
        )
        q3 = datamodels.LessonQA(
            lesson=l1, question="Why 3?", answer="Because you can do 3!", order=3
        )
        l1.questions.append(q1)
        l1.questions.append(q2)
        l1.questions.append(q3)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.questions), 3)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/qa/{}/delete".format(l1.id, q1.id),
            user=user,
            expected_status_code=200,
        )
        self.assertEqual(len(l1.questions), 2)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["message"], "Question deleted")

        # Check order
        self.assertEqual(q2.order, 1)
        self.assertEqual(q3.order, 2)

    def test_remove_wrong_question(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()
        question = datamodels.LessonQA(
            lesson=l1, question="Why?", answer="Because you can!"
        )
        l1.questions.append(question)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.questions), 1)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/qa/{}/delete".format(l1.id, 123),
            user=user,
            expected_status_code=400,
        )
        self.assertEqual(len(l1.questions), 1)
        self.assertFalse(response.json["success"])
        self.assertEqual(response.json["message"], "Wrong question or lesson")

    def test_reorder_questions(self):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()
        q1 = datamodels.LessonQA(
            lesson=l1, question="Why 1?", answer="Because you can do 1!", order=1
        )
        q2 = datamodels.LessonQA(
            lesson=l1, question="Why 2?", answer="Because you can do 2!", order=2
        )
        q3 = datamodels.LessonQA(
            lesson=l1, question="Why 3?", answer="Because you can do 3!", order=3
        )
        l1.questions.append(q1)
        l1.questions.append(q2)
        l1.questions.append(q3)
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.questions), 3)
        make_authorized_call(
            url="/course/abc-123/lessons/{}/qa/reorder".format(l1.id),
            user=user,
            data={"items_order": "{},{},{}".format(q3.id, q1.id, q2.id)},
            expected_status_code=200,
        )

        self.assertEqual(q1.order, 2)
        self.assertEqual(q2.order, 3)
        self.assertEqual(q3.order, 1)

    def validate_wrong_lesson_or_course(self, url):
        course = self.make_standard_course(guest_access=True)
        self.session.add(course)

        user = self.makeUser(email="home@teachers.com", id=1, username="the_teacher")
        self.session.add(user)
        self.session.commit()
        course.add_instructor(user)
        self.session.commit()
        l1 = self.make_standard_course_lesson(title="lesson 1", course=course, order=1)
        self.session.add(l1)
        self.session.commit()

        response = make_authorized_call(url=url, user=user, expected_status_code=400)

        self.assertEqual(response.json["message"], "Wrong lesson or course")

    def test_add_teacher_no_such_lesson(self):
        self.validate_wrong_lesson_or_course(
            url="/course/abc-123/lessons/123456789/teacher/add"
        )

    def test_remove_teacher_wrong_lesson(self):
        self.validate_wrong_lesson_or_course(
            url="/course/abc-123/lessons/{}/teacher/{}/delete".format(12345, 1)
        )

    def test_add_question_wrong_lesson(self):
        self.validate_wrong_lesson_or_course(
            url="/course/abc-123/lessons/{}/qa/add".format(12345)
        )

    def test_remove_question_wrong_lesson(self):
        self.validate_wrong_lesson_or_course(
            url="/course/abc-123/lessons/{}/qa/{}/delete".format(12345, 1)
        )

    def test_reorder_questions_wrong_lesson(self):
        self.validate_wrong_lesson_or_course(
            url="/course/abc-123/lessons/{}/qa/reorder".format(12345, 1)
        )
