import datetime
import unittest

import datamodels
from app import app


class TestModels(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

    def tearDown(self):
        datamodels._clear_session_for_tests()

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
        u.password = "password"
        return u

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
    def makeInstitute(
        obj_id=1,
        name="University of Super Heroes",
        slug="university_of_super_heroes",
        logo="link_to_fancy_url",
    ):
        institute = datamodels.Institute(name=name, id=obj_id, logo=logo, slug=slug)
        return institute

    def test_user_creation(self):
        u = self.makeUser(
            id=1,
            first_name="Marge",
            last_name="Simpson",
            email="marge@simpsons.com",
            password="password",
        )
        self.session.add(u)
        u2 = datamodels.get_user(1)
        self.assertEqual(u2.full_name, "Marge Simpson")
        self.assertEqual(u2.email, "marge@simpsons.com")
        self.assertTrue(u2.check_password, "password")

    def test_student_enrollment(self):
        u = self.makeUser(id=1)
        self.session.add(u)
        c = self.make_standard_course()
        self.session.add(c)
        c.enroll(u)
        u2 = datamodels.get_user(1)
        self.assertEqual(len(u2.courses), 1)
        self.assertEqual(u2.courses[0].id, 1)
        self.assertEqual(
            u2.course_enrollments[0].access_level, datamodels.COURSE_ACCESS_STUDENT
        )

    def test_users_teaches(self):
        u = self.makeUser(id=1)
        self.session.add(u)

        course = self.make_standard_course()
        self.session.add(course)

        self.assertFalse(u.teaches(course))
        course.enroll(u)
        self.assertFalse(u.teaches(course))

        u2 = self.makeUser(email="home@teachers.com", id=2, username="the_teacher")
        self.session.add(u2)
        course.add_instructor(u2)
        self.assertTrue(u2.teaches(course))

    def test_user_not_found(self):
        u = datamodels.get_user(1)
        self.assertIsNone(u)

    def test_course_creation(self):
        c = self.make_standard_course()
        self.session.add(c)
        c = datamodels.get_course_by_code("ABC123")
        c2 = datamodels.get_course_by_slug("abc-123")
        self.assertEqual(c.title, "Foo Course")
        self.assertEqual(c, c2)

    def test_public_course_creation(self):
        c = self.make_standard_course(
            code="DEF456", title="Bar Course", guest_access=True
        )
        self.session.add(c)
        c_results = datamodels.get_public_courses()
        for result in c_results:
            if result.course_code == "DEF456":
                c = result
        self.assertEqual(c.title, "Bar Course")

    def test_course_not_found(self):
        u = datamodels.get_course_by_code("ABC123")
        self.assertIsNone(u)

    def test_lesson_creation(self):
        c = self.make_standard_course()
        self.session.add(c)
        l = self.make_standard_course_lesson(course=c)
        self.session.add(l)
        l = datamodels.get_lesson(1)
        self.assertEqual(l.title, "Lesson")

    def test_segment_creation(self):
        c = self.make_standard_course()
        self.session.add(c)
        l = self.make_standard_course_lesson(course=c)
        self.session.add(l)
        s = self.make_segment(lesson=l)
        self.session.add(s)
        s = datamodels.get_segment(1)
        self.assertEqual(s.title, "Segment")

    def test_course_duration(self):
        course = self.make_standard_course()
        self.session.add(course)

        # Course without lessons have length of 0 seconds
        self.assertEqual(course.duration_seconds, 0)

        # Add a lesson to the course with a segment of non-zero duration
        lesson = self.make_standard_course_lesson(course=course)
        self.session.add(lesson)

        s = self.make_segment(lesson=lesson)
        self.session.add(s)

        self.assertEqual(course.duration_seconds, 200)

    def test_find_lesson_by_slug(self):
        course = self.make_standard_course()
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course=course)
        self.session.add(lesson)

        lesson2 = datamodels.get_lesson_by_slug(course.slug, lesson.slug)
        self.assertIsNotNone(lesson2)

        # No such lesson
        lesson2 = datamodels.get_lesson_by_slug(course.slug, "no_such_lesson")
        self.assertIsNone(lesson2)

    def test_get_lesson_thumbnail(self):
        course = self.make_standard_course()
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course=course)
        self.session.add(lesson)

        with self.assertRaises(Exception):
            thumbnail = lesson.thumbnail

        s1 = self.make_segment(lesson=lesson)
        s2 = self.make_segment(lesson=lesson, thumbnail="thumbnail_2")
        self.session.add(s1, s2)

        self.assertEqual(lesson.thumbnail, "thumbnail_1")

    def test_password(self):
        u = self.makeUser()
        self.session.add(u)
        self.assertEqual(u.password, "")

    def test_check_password(self):
        u = self.makeUser()
        self.session.add(u)
        self.assertTrue(u.check_password("password"))
        self.assertFalse(u.check_password("wrongpassword"))

    def test_preference(self):
        u = self.makeUser()
        self.session.add(u)

        # A user do not have particular preference
        preference = datamodels.UserPreference.get_preference(u, "emails_from_teachers")
        self.assertIsNone(preference)
        user_preference = u.preference("emails_from_teachers")
        self.assertFalse(user_preference)

        # Set a preference for a user
        u.set_preference("emails_from_teachers", True)
        user_preference = u.preference("emails_from_teachers")
        self.assertTrue(user_preference)

        # Get preference that do not exists
        with self.assertRaises(Exception):
            u.preference("there_is_no_such_preference")

    def test_institute_creation(self):
        institute = self.makeInstitute()
        self.session.add(institute)

        institute2 = datamodels.Institute.find_by_slug("university_of_super_heroes")
        self.assertEqual(institute2.name, "University of Super Heroes")
        self.assertEqual(institute2.logo, "link_to_fancy_url")

    def test_add_user_to_institute(self):
        institute = self.makeInstitute()
        self.session.add(institute)

        institute2 = datamodels.Institute.find_by_slug("university_of_super_heroes")
        self.assertEqual(len(institute2.users), 0)

        user = self.makeUser()
        self.session.add(user)

        institute2.add_user(user)
        self.assertEqual(
            len(self.session.query(datamodels.InstituteEnrollment).all()), 1
        )
        self.assertEqual(institute2.users[0].user.id, user.id)
        self.assertEqual(institute2.users[0].institute.id, institute2.id)
        self.assertEqual(institute2.users[0].access_level, 0)

    def test_program_creation(self):
        self.assertEqual(len(self.session.query(datamodels.Program).all()), 0)

        program = datamodels.Program(
            name="Entrepreneurship masters", slug="entrepreneurship"
        )
        self.session.add(program)

        program2 = datamodels.get_program_by_slug("entrepreneurship")
        self.assertEqual(program2.name, "Entrepreneurship masters")

    def test_program_enrollment(self):
        program = datamodels.Program(
            name="Entrepreneurship masters", slug="entrepreneurship"
        )
        self.session.add(program)
        program2 = datamodels.get_program_by_slug("entrepreneurship")

        user = self.makeUser()
        self.session.add(user)

        self.assertEqual(len(self.session.query(datamodels.ProgramEnrollment).all()), 0)
        program2.add_user(user)
        self.assertEqual(len(self.session.query(datamodels.ProgramEnrollment).all()), 1)
        self.assertEqual(program2.users[0].user.id, user.id)

    def test_get_segment_progress(self):
        course = self.make_standard_course()
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course=course)
        self.session.add(lesson)
        user = self.makeUser()
        segment = self.make_segment(lesson=lesson)
        self.session.add(user, segment)

        # User doesn't have any progress
        self.assertIsNone(datamodels.get_segment_progress(segment.id, user.id))
        self.assertEqual(segment.user_progress(None), 0)
        self.assertEqual(segment.user_progress(user), 0)

        # User has progress
        progress = datamodels.SegmentUserProgress(
            user_id=user.id, segment_id=segment.id, progress=20
        )
        self.session.add(progress)

        progress = datamodels.get_segment_progress(segment.id, user.id)
        self.assertIsInstance(progress, datamodels.SegmentUserProgress)
        self.assertEqual(progress.progress, 20)
        self.assertEqual(segment.user_progress(user), 20)

    def test_save_progress(self):
        course = self.make_standard_course()
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course=course)
        self.session.add(lesson)
        user = self.makeUser()
        segment = self.make_segment(lesson=lesson)
        self.session.add(user, segment)

        self.assertEqual(segment.user_progress(user), 0)
        datamodels.save_segment_progress(segment.id, user.id, 30)
        self.assertEqual(segment.user_progress(user), 30)
        datamodels.save_segment_progress(segment.id, user.id, 50)
        self.assertEqual(segment.user_progress(user), 50)

    def test_lesson_progress(self):
        course = self.make_standard_course()
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course=course)
        self.session.add(lesson)
        user = self.makeUser()
        self.session.add(user)
        seg_a = self.make_segment(lesson=lesson)
        seg_b = self.make_segment(lesson=lesson)
        self.session.add(seg_a)
        self.session.add(seg_b)
        self.assertEqual(len(lesson.segments), 2)

        self.assertEqual(lesson.user_progress_percent(user), 0)
        seg_a.save_user_progress(user, 30)
        self.assertEqual(lesson.user_progress_list(user), [30, 0])
        self.assertEqual(lesson.user_progress_percent(user), 15)
        seg_b.save_user_progress(user, 30)
        self.assertEqual(lesson.user_progress_list(user), [30, 30])
        self.assertEqual(lesson.user_progress_percent(user), 30)

        user_b = self.makeUser(id=2, username="marge", email="marge@example.com")
        self.session.add(user_b)
        self.assertEqual(lesson.user_progress_percent(user_b), 0)
        self.assertEqual(lesson.user_progress_list(user_b), [0, 0])

    def test_course_progress_aggregate_by_user(self):
        course = self.make_standard_course()
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course=course)
        lesson_b = self.make_standard_course_lesson(course=course)
        self.session.add(lesson)
        self.session.add(lesson_b)
        user = self.makeUser()
        self.session.add(user)
        seg_a = self.make_segment(lesson=lesson)
        seg_b = self.make_segment(lesson=lesson)
        seg_c = self.make_segment(lesson=lesson_b)
        seg_d = self.make_segment(lesson=lesson_b)
        self.session.add(seg_a)
        self.session.add(seg_b)
        self.session.add(seg_c)
        self.session.add(seg_d)

        self.assertEqual(course.user_progress(user), 0)
        seg_a.save_user_progress(user, 20)
        self.assertEqual(course.user_progress(user), 5)

    def test_user_total_course_progress(self):
        course = self.make_standard_course()
        course_b = datamodels.Course(title="foo", course_code="abccc", slug="abccc")
        self.session.add(course)
        self.session.add(course_b)
        lesson = self.make_standard_course_lesson(course=course)
        lesson_b = self.make_standard_course_lesson(course=course_b)
        self.session.add(lesson)
        self.session.add(lesson_b)
        user = self.makeUser()
        self.session.add(user)
        seg_a = self.make_segment(lesson=lesson)
        seg_b = self.make_segment(lesson=lesson)
        seg_c = self.make_segment(lesson=lesson_b)
        seg_d = self.make_segment(lesson=lesson_b)
        self.session.add(seg_a)
        self.session.add(seg_b)
        self.session.add(seg_c)
        self.session.add(seg_d)
        course.enroll(user)
        course_b.enroll(user)
        self.assertEqual(user.course_progress, 0)

        self.assertEqual(user.course_progress, 0)
        seg_a.save_user_progress(user, 20)
        self.assertEqual(user.course_progress, 5)

    def test_resource_access_log(self):
        course = self.make_standard_course()
        self.session.add(course)
        lesson = self.make_standard_course_lesson(course=course)
        self.session.add(lesson)
        user_a = self.makeUser(id=1)
        user_b = self.makeUser(id=2, username="marge", email="marge@simpsons.com")
        resource_a = datamodels.Resource(lesson=lesson, title="Some Resource")
        resource_b = datamodels.Resource(lesson=lesson, title="Other Resource")

        self.session.add(user_a)
        self.session.add(user_b)
        self.session.add(resource_a)
        self.session.add(resource_b)

        self.session.commit()

        self.assertEqual(resource_a.total_views, 0)
        resource_a.log_user_view(user_a)
        self.assertEqual(resource_a.views_by_user(user_a), 1)
        self.assertEqual(resource_a.total_views, 1)
        resource_a.log_user_view(user_a)
        self.assertEqual(resource_a.views_by_user(user_a), 2)
        self.assertEqual(resource_a.total_views, 2)
        resource_a.log_user_view(user_a)
        self.assertEqual(resource_a.views_by_user(user_a), 3)
        self.assertEqual(resource_a.total_views, 3)
        resource_a.log_user_view(user_a)
        self.assertEqual(resource_a.views_by_user(user_a), 4)
        self.assertEqual(resource_a.total_views, 4)
        resource_a.log_user_view(user_a)
        self.assertEqual(resource_a.views_by_user(user_a), 5)
        self.assertEqual(resource_a.total_views, 5)

        resource_a.log_user_view(user_b)
        self.assertEqual(resource_a.views_by_user(user_b), 1)
        self.assertEqual(resource_a.total_views, 6)

        self.assertEqual(resource_b.views_by_user(user_a), 0)
        self.assertEqual(resource_b.views_by_user(user_b), 0)
        self.assertEqual(resource_b.total_views, 0)

        resource_a.log_anonymous_view()
        self.assertEqual(resource_a.total_views, 7)
