import json

import unittest
import datamodels
from app import app

from .utils import ObjectsGenerator
from datamodels.enums import SegmentBarrierEnum, SegmentStatus


class TestUserProgress(ObjectsGenerator, unittest.TestCase):
    def setUp(self):
        with app.app_context():
            self.session = datamodels.get_session()

            self.course = self.make_standard_course(guest_access=True)
            self.session.add(self.course)

            self.user = self.makeUser(
                email="emma@students.com", id=1, username="the_student"
            )
            self.session.add(self.user)
            self.session.commit()
            self.course.enroll(self.user)

            self.l0 = self.make_standard_course_lesson(
                title="Intro lesson", course=self.course, order=0
            )
            self.session.add(self.l0)
            self.l0s0 = self.make_segment(
                self.l0,
                title="Intro segment",
                order=0,
                slug="intro-segment",
                type="video",
            )
            self.session.add(self.l0s0)

            self.l1 = self.make_standard_course_lesson(
                title="lesson 1", course=self.course, order=1
            )
            self.session.add(self.l1)
            self.l1s1 = self.make_segment(
                self.l1,
                title="Intro segment l1",
                order=0,
                slug="intro-segment-l1",
                type="text",
            )
            self.l1s2 = self.make_segment(
                self.l1, title="Segment l1s1", order=1, slug="segment-1"
            )
            self.l1s3 = self.make_segment(
                self.l1, title="Segment l1s2", order=2, slug="segment-2"
            )
            self.session.add(self.l1s1)
            self.session.add(self.l1s2)
            self.session.add(self.l1s3)

            self.l2 = self.make_standard_course_lesson(
                title="lesson 2", course=self.course, order=2
            )
            self.session.add(self.l2)
            self.l2s1 = self.make_segment(
                self.l2,
                title="Intro segment l2",
                order=0,
                slug="intro-segment-l2",
                type="text",
            )
            self.l2s2 = self.make_segment(
                self.l2, title="Segment l2s1", order=1, slug="segment-1"
            )
            self.l2s3 = self.make_segment(
                self.l2, title="Segment l2s2", order=2, slug="segment-2"
            )
            self.session.add(self.l2s1)
            self.session.add(self.l2s2)
            self.session.add(self.l2s3)

    def tearDown(self):
        datamodels._clear_session_for_tests()

    # def test_two_soft_barriers_first_done(self):
    #
    #     self.session.commit()
    #     self.l1s2.permission = SegmentBarrierEnum.barrier
    #     self.l2s2.permission = SegmentBarrierEnum.barrier
    #     self.session.add(self.l1s2)
    #     self.session.add(self.l2s2)
    #     self.session.commit()
    #
    #     print("++++")
    #     print(self.l2s1.order, self.l2s1.lesson.order, self.l2s1.lesson_id)
    #     a = self.l2s1.locked(self.user)
    #     print(a)
    #     print("++++")
    #     self.assertTrue(False)
    #     #self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.locked)

    def test_all_segments_are_accessible(self):
        """
        When a course doesn't have barriers all lessons should be accessible from any point.
        """
        self.session.commit()

        segments = datamodels.Segment.objects().all()

        self.assertEqual(len(segments), 7)

        for segment in segments:
            self.assertEqual(segment.user_status(self.user), SegmentStatus.accessible)

    def test_soft_barrier_not_done(self):
        """
        When a course has a soft barrier, which wasn't finished by student then all subsequent segments are locked
        including lessons after this segment.
        """

        self.l1s2.barrier = SegmentBarrierEnum.barrier
        self.session.add(self.l1s2)
        self.session.commit()

        self.assertEqual(self.l0s0.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l1s1.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(
            self.l1s2.user_status(self.user), SegmentStatus.accessible
        )  # we should be able to make barrier segment
        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s2.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s3.user_status(self.user), SegmentStatus.locked)

    def test_soft_barrier_done(self):
        """
        When a course has a soft barrier, which was finished by student then all subsequent segments are accessible.
        """
        self.l1s2.barrier = SegmentBarrierEnum.barrier
        self.session.add(self.l1s2)
        self.session.commit()

        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s2.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s3.user_status(self.user), SegmentStatus.locked)

        self.assertEqual(self.l1s2.user_status(self.user), SegmentStatus.accessible)
        progress = datamodels.SegmentUserProgress(
            progress=97, segment_id=self.l1s2.id, user_id=self.user.id
        )
        self.session.add(progress)
        self.session.commit()
        self.assertEqual(self.l1s2.user_status(self.user), SegmentStatus.completed)
        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l2s2.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l2s3.user_status(self.user), SegmentStatus.accessible)

    def test_two_soft_barriers_first_done(self):
        """
        When a course have at least two soft barriers. Assume that first is done by student, then:
        -- all segments between the first and the second barrier are accessible
        -- all segments after the second barrier are locked
        """
        self.session.commit()
        self.l1s2.barrier = SegmentBarrierEnum.barrier
        self.l2s2.barrier = SegmentBarrierEnum.barrier
        self.session.add(self.l1s2)
        self.session.add(self.l2s2)
        self.session.commit()

        self.assertEqual(self.l1s1.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l1s2.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s2.user_status(self.user), SegmentStatus.locked)
        progress = datamodels.SegmentUserProgress(
            progress=97, segment_id=self.l1s2.id, user_id=self.user.id
        )
        self.session.add(progress)
        self.session.commit()
        self.assertEqual(self.l1s1.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l1s2.user_status(self.user), SegmentStatus.completed)
        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l2s2.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l2s3.user_status(self.user), SegmentStatus.locked)

    def test_soft_barrier_blocking(self):
        """
        A course has a hard barrier. Assume that at least one segment prior the hard barrier is not completed then all
         segments after the hard barrier are locked.
        """
        self.l1s2.barrier = SegmentBarrierEnum.barrier
        self.session.add(self.l1s2)
        self.session.commit()

        progress1 = datamodels.SegmentUserProgress(
            progress=98, segment_id=self.l0s0.id, user_id=self.user.id
        )
        progress2 = datamodels.SegmentUserProgress(
            progress=57, segment_id=self.l1s1.id, user_id=self.user.id
        )
        self.session.add(progress1)
        self.session.add(progress2)
        self.session.commit()
        self.assertEqual(self.l0s0.user_status(self.user), SegmentStatus.completed)
        self.assertEqual(self.l1s1.user_status(self.user), SegmentStatus.touched)
        self.assertEqual(self.l1s2.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.locked)

    def test_hard_barrier_is_blocking(self):
        """
        A course has a hard barrier. Assume that at least one segment prior the hard barrier is not completed then all
         segments after the hard barrier are locked.
        """
        self.l1s2.barrier = SegmentBarrierEnum.hard_barrier
        self.session.add(self.l1s2)
        self.session.commit()

        progress1 = datamodels.SegmentUserProgress(
            progress=98, segment_id=self.l0s0.id, user_id=self.user.id
        )
        progress2 = datamodels.SegmentUserProgress(
            progress=57, segment_id=self.l1s1.id, user_id=self.user.id
        )
        self.session.add(progress1)
        self.session.add(progress2)
        self.session.commit()
        self.assertEqual(self.l0s0.user_status(self.user), SegmentStatus.completed)
        self.assertEqual(self.l1s1.user_status(self.user), SegmentStatus.touched)
        self.assertEqual(self.l1s2.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.locked)

        # Hard barrier requires all prior segments to be completed.
        progress2.progress = 99
        self.session.add(progress2)
        self.session.commit()
        self.assertEqual(self.l1s1.user_status(self.user), SegmentStatus.completed)
        self.assertEqual(self.l1s2.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.locked)

    def test_hard_barrier_completed(self):
        """
        A course has a hard barrier. Assume all segments prior the hard barrier are completed. Before completing
        the hard barrier all segments after it are locked. A student completes the hard barrier. All segments after it
        are accessible.
        """
        self.l1s2.barrier = SegmentBarrierEnum.hard_barrier
        self.session.add(self.l1s2)
        self.session.commit()

        progress1 = datamodels.SegmentUserProgress(
            progress=98, segment_id=self.l0s0.id, user_id=self.user.id
        )
        progress2 = datamodels.SegmentUserProgress(
            progress=99, segment_id=self.l1s1.id, user_id=self.user.id
        )
        self.session.add(progress1)
        self.session.add(progress2)
        self.session.commit()
        self.assertEqual(self.l0s0.user_status(self.user), SegmentStatus.completed)
        self.assertEqual(self.l1s1.user_status(self.user), SegmentStatus.completed)
        self.assertEqual(self.l1s2.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s2.user_status(self.user), SegmentStatus.locked)
        self.assertEqual(self.l2s3.user_status(self.user), SegmentStatus.locked)
        # A student completes a hard barrier
        progress1 = datamodels.SegmentUserProgress(
            progress=98, segment_id=self.l1s2.id, user_id=self.user.id
        )
        self.session.add(progress1)
        self.session.commit()
        self.assertEqual(self.l1s2.user_status(self.user), SegmentStatus.completed)
        self.assertEqual(self.l1s3.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l2s1.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l2s2.user_status(self.user), SegmentStatus.accessible)
        self.assertEqual(self.l2s3.user_status(self.user), SegmentStatus.accessible)

    def test_merge_data_after_login(self):
        self.session.commit()
        s = app.test_client()

        with s.session_transaction() as sess:
            sess["anon_progress"] = json.dumps({self.l1s1.id: 35})

        s.post("/login", data={"email": self.user.email, "password": "password"})

        with s.session_transaction() as sess:
            self.assertEqual(sess["user_id"], self.user.id)
            with self.assertRaises(KeyError):
                sess["anon_progress"]

        self.assertEqual(
            datamodels.SegmentUserProgress.find_user_progress(
                self.l1s1.id, self.user.id
            ).progress,
            35,
        )

    def test_merge_data_after_register(self):
        # ToDo: add this test
        pass

    def test_add_enrollment_after_register(self):
        # ToDo: add this test
        pass
