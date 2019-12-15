import unittest
import datamodels
from app import app
import re

from .utils import make_authorized_call, ObjectsGenerator
from datamodels.enums import VideoTypeEnum, SegmentPermissionEnum


class TestSegmentsRoutes(ObjectsGenerator, unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

            self.course = self.make_standard_course(guest_access=True)
            self.session.add(self.course)

            self.user = self.makeUser(
                email="home@teachers.com", id=1, username="the_teacher"
            )
            self.session.add(self.user)
            self.session.commit()
            self.course.add_instructor(self.user)

    def tearDown(self):
        datamodels._clear_session_for_tests()

    def test_change_order_of_intro_segment(self):
        l1 = self.make_standard_course_lesson(
            title="lesson 1", course=self.course, order=1
        )
        self.session.add(l1)
        s1 = self.make_segment(l1, title="Segment Intro", order=0, slug="segment-intro")
        s2 = self.make_segment(l1, title="Segment 1", order=1, slug="segment-1")
        s3 = self.make_segment(l1, title="Segment 2", order=2, slug="segment-2")
        self.session.add(s1)
        self.session.add(s2)
        self.session.add(s3)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/reorder".format(l1.id),
            user=self.user,
            data={"items_order": "{},{}".format(s2.id, s1.id)},
            expected_status_code=400,
        )

        self.assertEqual(response.json["message"], "Wrong number of items")

    def test_reorder_segments_lesson_not_in_course(self):
        course2 = self.make_standard_course(
            guest_access=True, slug="course-2", code="course2", title="course 2"
        )
        self.session.add(course2)

        l1 = self.make_standard_course_lesson(title="lesson 1", course=course2, order=1)
        self.session.add(l1)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/reorder".format(l1.id),
            user=self.user,
            data={"items_order": "1,2"},
            expected_status_code=400,
        )

        self.assertEqual(response.json["message"], "Course does not match lesson")

    def test_change_segment_order(self):
        l1 = self.make_standard_course_lesson(
            title="lesson 1", course=self.course, order=1
        )
        self.session.add(l1)
        s1 = self.make_segment(l1, title="Segment Intro", order=0, slug="segment-intro")
        s2 = self.make_segment(l1, title="Segment 1", order=1, slug="segment-1")
        s3 = self.make_segment(l1, title="Segment 2", order=2, slug="segment-2")
        self.session.add(s1)
        self.session.add(s2)
        self.session.add(s3)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/reorder".format(l1.id),
            user=self.user,
            data={"items_order": "{},{}".format(s3.id, s2.id)},
            expected_status_code=200,
        )

        self.assertEqual(response.json["message"], "Order updated")
        self.assertEqual(self.session.query(datamodels.Segment).get(s3.id).order, 1)
        self.assertEqual(self.session.query(datamodels.Segment).get(s2.id).order, 2)

    def test_delete_segment(self):
        l1 = self.make_standard_course_lesson(
            title="lesson 1", course=self.course, order=1
        )
        self.session.add(l1)
        s1 = self.make_segment(l1, title="Segment Intro", order=0, slug="segment-intro")
        s2 = self.make_segment(l1, title="Segment 1", order=1, slug="segment-1")
        s3 = self.make_segment(l1, title="Segment 2", order=2, slug="segment-2")
        self.session.add(s1)
        self.session.add(s2)
        self.session.add(s3)
        self.session.commit()

        self.assertEqual(len(l1.segments), 3)

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/{}/delete".format(l1.id, s3.id),
            user=self.user,
            data={},
            expected_status_code=200,
        )

        self.assertEqual(len(l1.segments), 2)
        self.assertEqual(
            response.json["success_url"],
            "/course/abc-123/lessons/{}/edit".format(l1.id),
        )
        segments = datamodels.Segment.get_ordered_items()
        self.assertEqual(segments[0].order, 0)
        self.assertEqual(segments[0].title, "Segment Intro")
        self.assertEqual(segments[1].order, 1)
        self.assertEqual(segments[1].title, "Segment 1")

    def test_delete_wrong_segment_id(self):
        l1 = self.make_standard_course_lesson(
            title="lesson 1", course=self.course, order=1
        )
        self.session.add(l1)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/1000000000/delete".format(l1.id),
            user=self.user,
            data={},
            expected_status_code=400,
        )

        self.assertFalse(response.json["success"])

    def test_delete_segment_not_in_course(self):

        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0
        )
        l2 = self.make_standard_course_lesson(
            title="other lesson", course=self.course, order=1
        )
        self.session.add(l1)
        self.session.add(l2)
        s1 = self.make_segment(l1, title="Segment Intro", order=0, slug="segment-intro")
        s2 = self.make_segment(
            l2, title="Segment Intro 2", order=0, slug="segment-intro-2"
        )
        self.session.add(s1)
        self.session.add(s2)
        self.session.commit()

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/{}/delete".format(l1.id, s2.id),
            user=self.user,
            data={},
            expected_status_code=400,
        )

        self.assertFalse(response.json["success"])

    def test_add_segment_wrong_lesson(self):
        l1 = self.make_standard_course_lesson(
            title="Some lesson", course=self.course, order=0
        )
        self.session.add(l1)
        c2 = self.make_standard_course(code="123456", slug="123456", title="Bar Course")
        self.session.add(c2)
        l2 = self.make_standard_course_lesson(
            title="Some other lesson", course=c2, order=0
        )
        self.session.add(l2)
        self.session.commit()

        self.assertEqual(len(l1.segments), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/text".format(l2.id),
            user=self.user,
            data={},
            expected_status_code=400,
        )

        self.assertEqual(len(l1.segments), 0)
        self.assertEqual("Lesson do not match course", response.json["message"])

    def test_add_text_segment(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0
        )
        self.session.add(l1)
        self.session.commit()

        data = {
            "segment_name": "Segment numero 1",
            "text_segment_content": "This is the second segment. The one after our brilliant intro.",
        }

        self.assertEqual(len(l1.segments), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/text".format(l1.id),
            user=self.user,
            data=data,
            expected_status_code=200,
        )

        self.assertEqual(len(l1.segments), 1)
        self.assertEqual(l1.segments[0].title, data["segment_name"])
        self.assertEqual(l1.segments[0].text, data["text_segment_content"])
        self.assertEqual(l1.segments[0].order, 1)
        self.assertTrue(
            re.search("Segment Segment numero 1 added", response.get_data(as_text=True))
        )

    def test_add_text_segment_without_data(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0
        )
        self.session.add(l1)
        self.session.commit()

        self.assertEqual(len(l1.segments), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/text".format(l1.id),
            user=self.user,
            data={},
            expected_status_code=400,
        )
        self.assertEqual(len(l1.segments), 0)
        # Can't create segment with such name
        self.assertTrue(
            re.search("create segment with such name.", response.json["message"])
        )

        data = {"segment_name": "Segment numero 1"}
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/text".format(l1.id),
            user=self.user,
            data=data,
            expected_status_code=400,
        )
        self.assertEqual(len(l1.segments), 0)
        print(response.json)
        self.assertTrue(
            re.search("Segment description is required", response.json["message"])
        )

        data = {
            "segment_name": "",
            "text_segment_content": "This is the second segment. The one after our brilliant intro.",
        }
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/text".format(l1.id),
            user=self.user,
            data=data,
            expected_status_code=400,
        )
        self.assertEqual(len(l1.segments), 0)
        self.assertTrue(
            re.search("create segment with such name.", response.json["message"])
        )

    def test_add_video_segment(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0
        )
        self.session.add(l1)
        self.session.commit()

        data = {
            "segment_name": "Video segment",
            "segment_url": "youtube.com/important_lesson_of_life",
        }

        self.assertEqual(len(l1.segments), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/video".format(l1.id),
            user=self.user,
            data=data,
            expected_status_code=200,
        )

        self.assertEqual(len(l1.segments), 1)
        self.assertEqual(l1.segments[0].title, data["segment_name"])
        self.assertEqual(l1.segments[0].video_type, VideoTypeEnum.standard)
        self.assertEqual(l1.segments[0].permission, SegmentPermissionEnum.normal)
        self.assertEqual(l1.segments[0].order, 1)
        self.assertTrue(
            re.search("Segment Video segment added", response.json["message"])
        )

    def test_add_video_segment_without_data(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0
        )
        self.session.add(l1)
        self.session.commit()

        data = {"segment_name": "Intro segment", "segment_url": ""}

        self.assertEqual(len(l1.segments), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/intro_text".format(l1.id),
            user=self.user,
            data={},
            expected_status_code=400,
        )

        self.assertEqual(len(l1.segments), 0)

    def test_add_intro_video_segment(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0
        )
        self.session.add(l1)
        self.session.commit()
        s1 = self.make_segment(title="intro", lesson=l1, order=1)
        self.session.add(s1)
        self.session.commit()

        data = {
            "segment_url": "https://youtube.com/some-video",
            "text_segment_content": "This is the second segment. The one after our brilliant intro.",
        }

        self.assertEqual(len(l1.segments), 1)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/intro_video".format(l1.id),
            user=self.user,
            data=data,
            expected_status_code=200,
        )

        self.assertEqual(len(l1.segments), 2)
        self.assertEqual(l1.segments[1].title, "Intro segment")
        self.assertEqual(l1.segments[1].text, data["text_segment_content"])
        self.assertEqual(l1.segments[1].url, data["segment_url"])
        self.assertEqual(l1.segments[1].order, 0)

    def test_add_segment_wrong_content_type(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0
        )
        self.session.add(l1)
        self.session.commit()

        data = {
            "segment_name": "Intro segment",
            "text_segment_content": "This is the second segment. The one after our brilliant intro.",
        }

        self.assertEqual(len(l1.segments), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/some_action".format(l1.id),
            user=self.user,
            data=data,
            expected_status_code=400,
        )

        self.assertEqual(len(l1.segments), 0)
        self.assertEqual("Wrong action", response.json["message"])

    def test_add_segment_order(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0
        )
        self.session.add(l1)
        self.session.commit()
        s1 = self.make_segment(
            title="The first segment", lesson=l1, order=1, slug="segment-1"
        )
        s2 = self.make_segment(
            title="The second segment", lesson=l1, order=2, slug="segment-2"
        )
        self.session.add(s1)
        self.session.add(s2)
        self.session.commit()

        data = {
            "segment_name": "The third segment",
            "text_segment_content": "This is the second segment. The one after our brilliant intro.",
        }

        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/text".format(l1.id),
            user=self.user,
            data=data,
            expected_status_code=200,
            follow_redirects=True,
        )

        segment = datamodels.get_segment_by_slug(
            "abc-123", l1.slug, "the-third-segment"
        )
        self.assertIsNotNone(segment)
        self.assertEqual(segment.order, 3)

    def test_add_segment_same_slug_same_lesson(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0
        )
        self.session.add(l1)
        self.session.commit()
        title = "This is the life"
        s1 = self.make_segment(title=title, lesson=l1, order=1)
        self.session.add(s1)
        self.session.commit()

        data = {
            "segment_name": title,
            "text_segment_content": "This is the second segment. The one after our brilliant intro.",
        }

        self.assertEqual(len(l1.segments), 1)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/text".format(l1.id),
            user=self.user,
            data=data,
            expected_status_code=400,
        )
        self.assertEqual(len(l1.segments), 1)
        # Can't create segment with such name
        self.assertEqual(
            "Can't create segment with such name.", response.json["message"]
        )

    def test_add_segment_same_slug_different_lesson(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0, slug="intro"
        )
        l2 = self.make_standard_course_lesson(
            title="some lesson", course=self.course, order=1, slug="some-lesson"
        )
        self.session.add(l1)
        self.session.add(l2)
        self.session.commit()
        title = "This is the life"
        s1 = self.make_segment(title=title, lesson=l1, order=1)
        self.session.add(s1)
        self.session.commit()

        data = {
            "segment_name": title,
            "text_segment_content": "This is the second segment. The one after our brilliant intro.",
        }

        self.assertEqual(len(l1.segments), 1)
        self.assertEqual(len(l2.segments), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/add/text".format(l2.id),
            user=self.user,
            data=data,
            expected_status_code=200,
            follow_redirects=True,
        )
        self.assertEqual(len(l1.segments), 1)
        self.assertEqual(len(l2.segments), 1)

    def test_copy_segment_wrong_lesson(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0, slug="intro"
        )
        l2 = self.make_standard_course_lesson(
            title="some lesson", course=self.course, order=1, slug="some-lesson"
        )
        self.session.add(l1)
        self.session.commit()
        s1 = self.make_segment(title="This is the life", lesson=l1, order=1)
        self.session.add(s1)
        self.session.commit()

        self.assertEqual(len(l1.segments), 1)
        self.assertEqual(len(l2.segments), 0)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/{}/copy".format(l2.id, s1.id),
            user=self.user,
            expected_status_code=200,
            follow_redirects=True,
            method="get",
        )
        self.assertEqual(len(l1.segments), 1)
        self.assertEqual(len(l2.segments), 0)
        self.assertTrue(
            re.search(
                "Lesson or segment do not match course or lesson",
                response.get_data(as_text=True),
            )
        )

    def test_copy_text_segment(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0, slug="intro"
        )
        self.session.add(l1)
        self.session.commit()
        s1 = self.make_segment(title="This is the life", lesson=l1, order=1)
        self.session.add(s1)
        self.session.commit()

        self.assertEqual(len(l1.segments), 1)
        response = make_authorized_call(
            url="/course/abc-123/lessons/{}/segments/{}/copy".format(l1.id, s1.id),
            user=self.user,
            expected_status_code=200,
            follow_redirects=True,
            method="get",
        )
        self.assertEqual(len(l1.segments), 2)
        s2 = l1.segments[1]
        self.assertTrue(s2.id != s1.id)
        self.assertEqual(s1.duration_seconds, s2.duration_seconds)
        self.assertEqual(s1.title + "_copy", s2.title)
        self.assertEqual(s2.order, 2)
        self.assertEqual(s1.text, s2.text)
        self.assertEqual(s1.type, s2.type)
        self.assertEqual(s1.permission, s2.permission)
        self.assertTrue(
            re.search("Segment duplicated", response.get_data(as_text=True))
        )

    def test_get_segment_veiw(self):
        l1 = self.make_standard_course_lesson(
            title="intro", course=self.course, order=0, slug="intro"
        )
        l2 = self.make_standard_course_lesson(
            title="some lesson", course=self.course, order=1, slug="some-lesson"
        )
        self.session.add(l1)
        self.session.commit()
        s1 = self.make_segment(title="This is the life", lesson=l1, order=1)
        self.session.add(s1)
        self.session.commit()

        make_authorized_call(
            url="/course/{}/{}/{}".format("wrong-slug", l1.slug, s1.slug),
            user=self.user,
            expected_status_code=404,
            method="get",
        )

        make_authorized_call(
            url="/course/abc-123/{}/{}".format("wrong-slug", s1.slug),
            user=self.user,
            expected_status_code=404,
            method="get",
        )

        make_authorized_call(
            url="/course/abc-123/{}/{}".format(l1.slug, "wrong-slug"),
            user=self.user,
            expected_status_code=404,
            method="get",
        )

        make_authorized_call(
            url="/course/abc-123/{}/{}".format(l1.slug, s1.slug),
            user=self.user,
            expected_status_code=200,
            follow_redirects=True,
            method="get",
        )
