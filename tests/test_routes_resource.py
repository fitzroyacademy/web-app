import re
import unittest

import datamodels
from app import app
from .utils import make_authorized_call, ObjectsGenerator


class TestSegmentsRoutes(ObjectsGenerator, unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()
            self.set_basic_course()

            self.lesson1 = self.make_standard_course_lesson(
                course=self.course, title="First lesson", order=1
            )
            self.lesson2 = self.make_standard_course_lesson(
                course=self.course, title="Second lesson", order=2
            )
            self.session.add(self.lesson1)
            self.session.add(self.lesson2)
            self.l1s1 = self.make_segment(self.lesson1, title="Segment Intro", order=0)
            self.l1s2 = self.make_segment(self.lesson1, title="Segment 1", order=1)
            self.l2s1 = self.make_segment(self.lesson2, title="Segment Intro", order=0)
            self.session.commit()

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def test_unauthorized_calls_or_not_a_teacher(self):
        s = app.test_client()
        urls = [
            ("/course/abc-123/lessons/1/resources/1/copy", "get"),
            ("/course/abc-123/lessons/1/resources/1/delete", "post"),
            ("/course/abc-123/lessons/1/resources/reorder", "post"),
            ("/course/abc-123/lessons/1/resources/reorder", "post"),
            ("/course/abc-123/lessons/1/resources/1/edit", "post"),
            ("/course/abc-123/lessons/1/resources/1/edit", "get"),
            ("/course/abc-123/lessons/1/resources/add", "post"),
        ]

        for url in urls:
            response = s.get(url[0]) if url[1] == "get" else s.post(url[0])
            self.assertEqual(response.status_code, 401)

        user = self.makeUser(email="home@not-a-teacher.com", id=2, username="the_user")
        self.session.add(user)
        self.session.commit()

        for url in urls:
            make_authorized_call(url[0], user, method=url[1], expected_status_code=404)

    def test_delete_resource(self):
        r1 = self.make_resource(self.lesson1, order=1)
        r2 = self.make_resource(self.lesson1, order=2)
        r3 = self.make_resource(self.lesson1, order=3)
        self.session.add(r1)
        self.session.add(r2)
        self.session.add(r3)
        self.session.commit()

        self.assertEqual(len(self.lesson1.resources), 3)
        self.assertEqual(r2.order, 2)
        self.assertEqual(r3.order, 3)
        response = make_authorized_call(
            url="/course/{}/lessons/{}/resources/{}/delete".format(
                self.course.slug, self.lesson1.id, r1.id
            ),
            user=self.user,
            expected_status_code=200,
        )
        self.assertEqual(
            response.json["success_url"],
            "/course/{}/lessons/{}/edit".format(self.course.slug, self.lesson1.id),
        )
        self.assertEqual(len(self.lesson1.resources), 2)
        self.assertEqual(r2.order, 1)
        self.assertEqual(r3.order, 2)

    def test_delete_resource_wrong_lesson(self):
        r1 = self.make_resource(self.lesson2, order=1)
        self.session.add(r1)
        self.session.commit()

        self.assertEqual(len(self.lesson2.resources), 1)
        response = make_authorized_call(
            url="/course/{}/lessons/{}/resources/{}/delete".format(
                self.course.slug, self.lesson1.id, r1.id
            ),
            user=self.user,
            expected_status_code=400,
        )
        self.assertEqual(len(self.lesson2.resources), 1)
        self.assertFalse(response.json["success"])

    def test_reorder_resources_wrong_lesson(self):
        make_authorized_call(
            url="/course/{}/lessons/{}/resources/reorder".format(
                self.course.slug, 1000000000
            ),
            user=self.user,
            data={"items_order": "1,2"},
            expected_status_code=400,
        )

    def test_change_order_of_resources(self):
        r1 = self.make_resource(self.lesson1, order=1)
        r2 = self.make_resource(self.lesson1, order=2)
        r3 = self.make_resource(self.lesson1, order=3)
        self.session.add(r1)
        self.session.add(r2)
        self.session.add(r3)
        self.session.commit()

        self.assertEqual(r1.order, 1)
        self.assertEqual(r2.order, 2)
        self.assertEqual(r3.order, 3)
        make_authorized_call(
            url="/course/{}/lessons/{}/resources/reorder".format(
                self.course.slug, self.lesson1.id, r1.id
            ),
            user=self.user,
            data={"items_order": "{},{},{}".format(r2.id, r1.id, r3.id)},
            expected_status_code=200,
        )
        self.assertEqual(r1.order, 2)
        self.assertEqual(r2.order, 1)
        self.assertEqual(r3.order, 3)

    def test_copy_resource_wrong_lesson(self):
        r1 = self.make_resource(self.lesson2, order=1)
        self.session.add(r1)
        self.session.commit()

        self.assertEqual(len(self.lesson1.resources), 0)
        self.assertEqual(len(self.lesson2.resources), 1)
        response = make_authorized_call(
            url="/course/{}/lessons/{}/resources/{}/copy".format(
                self.course.slug, self.lesson1.id, r1.id
            ),
            user=self.user,
            expected_status_code=200,
            method="get",
            follow_redirects=True,
        )
        self.assertEqual(len(self.lesson1.resources), 0)
        self.assertEqual(len(self.lesson2.resources), 1)
        self.assertTrue(
            re.search(
                "Lesson or resource do not match course or lesson",
                response.get_data(as_text=True),
            )
        )

    def test_copy_resource(self):
        r1 = self.make_resource(self.lesson1, order=1)
        self.session.add(r1)
        self.session.commit()

        self.assertEqual(len(self.lesson1.resources), 1)
        response = make_authorized_call(
            url="/course/{}/lessons/{}/resources/{}/copy".format(
                self.course.slug, self.lesson1.id, r1.id
            ),
            user=self.user,
            expected_status_code=200,
            method="get",
            follow_redirects=True,
        )

        self.assertEqual(len(self.lesson1.resources), 2)
        r2 = self.lesson1.resources[1]
        self.assertTrue(r1.id != r2.id)
        self.assertEqual(r1.title + "_copy", r2.title)
        self.assertEqual(r2.order, 2)
        self.assertEqual(r1.description, r2.description)
        self.assertEqual(r1.type, r2.type)
        self.assertEqual(r1.featured, r2.featured)
        self.assertEqual(r1.lesson_id, r2.lesson_id)

        self.assertTrue(
            re.search("Resource duplicated", response.get_data(as_text=True))
        )

    def test_edit_resource_wrong_lesson(self):
        r1 = self.make_resource(self.lesson2, order=1)
        self.session.add(r1)
        self.session.commit()

        response = make_authorized_call(
            url="/course/{}/lessons/{}/resources/{}/edit".format(
                self.course.slug, self.lesson1.id, r1.id
            ),
            user=self.user,
            expected_status_code=400,
            method="get",
        )
        self.assertEqual(response.json["message"], "Wrong lesson or resource")

    def test_retrive_resource(self):
        r1 = self.make_resource(self.lesson1, order=1)
        self.session.add(r1)
        self.session.commit()

        response = make_authorized_call(
            url="/course/{}/lessons/{}/resources/{}/edit".format(
                self.course.slug, self.lesson1.id, r1.id
            ),
            user=self.user,
            expected_status_code=200,
            method="get",
        )
        self.assertEqual(response.json["url"], r1.url)
        self.assertEqual(response.json["title"], r1.title)
        self.assertEqual(response.json["type"], r1.type.name)
        self.assertEqual(response.json["description"], r1.description)

    def test_add_edit_resource_no_such_lesson(self):
        make_authorized_call(
            url="/course/{}/lessons/{}/resources/{}/edit".format(
                self.course.slug, 100000000, 1
            ),
            user=self.user,
            expected_status_code=404,
        )

        make_authorized_call(
            url="/course/{}/lessons/{}/resources/add".format(
                self.course.slug, 10000000
            ),
            user=self.user,
            expected_status_code=404,
        )

    def test_add_resource(self):
        data = {
            "resource_url": "https://docs.google.com/blahblah",
            "resource_title": "Wonderful World",
            "resource_type": "google_doc",
            "resource_description": "Some fancy description",
        }

        self.assertEqual(len(self.lesson1.resources), 0)
        response = make_authorized_call(
            url="/course/{}/lessons/{}/resources/add".format(
                self.course.slug, self.lesson1.id
            ),
            data=data,
            user=self.user,
            expected_status_code=200,
            follow_redirects=True,
        )

        self.assertTrue(re.search("Resource created", response.get_data(as_text=True)))
        self.assertEqual(len(self.lesson1.resources), 1)
        r1 = self.lesson1.resources[0]

        self.assertEqual(r1.title, data["resource_title"])
        self.assertEqual(r1.description, data["resource_description"])
        self.assertEqual(r1.type.name, data["resource_type"])
        self.assertEqual(r1.url, data["resource_url"])
        self.assertEqual(r1.slug, "wonderful-world")

    def test_edit_resource(self):
        r1 = self.make_resource(lesson=self.lesson1)
        self.session.add(r1)
        self.session.commit()

        data = {
            "resource_url": r1.url,
            "resource_title": "Wonderful wonderland",
            "resource_type": r1.type.name,
            "resource_description": r1.description,
        }

        self.assertEqual(len(self.lesson1.resources), 1)
        response = make_authorized_call(
            url="/course/{}/lessons/{}/resources/{}/edit".format(
                self.course.slug, self.lesson1.id, r1.id
            ),
            data=data,
            user=self.user,
            expected_status_code=200,
            follow_redirects=True,
        )

        self.assertTrue(re.search("Resource updated", response.get_data(as_text=True)))
        self.assertEqual(len(self.lesson1.resources), 1)
        r1_updated = self.lesson1.resources[0]

        self.assertEqual(r1.id, r1_updated.id)
        self.assertEqual(r1_updated.title, data["resource_title"])
        self.assertEqual(r1_updated.description, data["resource_description"])
        self.assertEqual(r1_updated.type.name, data["resource_type"])
        self.assertEqual(r1_updated.url, data["resource_url"])
        self.assertEqual(r1_updated.slug, "wonderful-wonderland")

    def test_edit_wrong_lesson(self):
        r1 = self.make_resource(lesson=self.lesson1)
        self.session.add(r1)
        self.session.commit()

        make_authorized_call(
            url="/course/{}/lessons/{}/resources/{}/edit".format(
                self.course.slug, self.lesson2.id, r1.id
            ),
            data={},
            user=self.user,
            expected_status_code=404,
        )
