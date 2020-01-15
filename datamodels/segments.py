from datetime import timedelta

import requests
import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask import url_for

from .base import OrderedBase, Base
from .surveys import Survey, SurveyResponse
from .enums import (
    VideoTypeEnum,
    SegmentBarrierEnum,
    SegmentStatus,
    SegmentStatusThreshold,
    SegmentType,
)

from utils.images import fetch_thumbnail_from_wistia
from .progress import SegmentUserProgress


class BarrierSegment(Base):
    __abstract__ = True
    barrier = sa.Column(sa.Enum(SegmentBarrierEnum), nullable=True)
    user = None

    def can_view(self, user=None, anonymous_progress=None):
        return self.__can_view_dispatcher(user, anonymous_progress)

    def is_hidden_segment(self):
        return self.barrier == SegmentBarrierEnum.hidden

    def __can_view_dispatcher(self, user=None, anonymous_progress=None):

        if anonymous_progress is None or not isinstance(anonymous_progress, dict):
            anonymous_progress = {}

        perm_name = self.barrier.name
        handler = getattr(self, "_can_view_{}".format(perm_name), None)

        if handler is None:
            # Make sure that when new barrier type is added then there is a handler
            raise NotImplementedError(
                "Dispatcher for permission {} not implemented".format(perm_name)
            )

        return handler(user, anonymous_progress)

    def _can_view_normal(self, user, anonymous_progress: dict):
        return True

    def _can_view_paid(self, user, anonymous_progress: dict):
        return False

    def _can_view_login(self, user, anonymous_progress: dict):
        return user is not None

    def _can_view_barrier(self, user, anonymous_progress: dict):
        progress = anonymous_progress.get(str(self.id), 0)
        return self.user_status(user, progress) == "completed"

    def _can_view_hard_barrier(self, user, anonymous_progress: dict):
        progress = anonymous_progress.get(str(self.id), 0)
        return self.user_status(user, progress) == "completed"

    def _can_view_hidden(self, user, anonymous_progress: dict):
        return user.teaches(self.lesson.course) if user else False

    def user_status(self, user, progress=None):

        if self.locked(user):
            return SegmentStatus.locked

        p = progress or self.user_progress(user)
        if p > SegmentStatusThreshold.completed:
            return SegmentStatus.completed
        if p > SegmentStatusThreshold.touched:
            return SegmentStatus.touched
        return SegmentStatus.accessible

    def get_prior_segments(self):
        qs = self.lesson.course.get_ordered_segments().filter(
            sa.or_(
                sa.and_(
                    self.lesson.__class__.order == self.lesson.order,
                    Segment.order < self.order,
                ),
                self.lesson.__class__.order < self.lesson.order,
            )
        )
        return qs

    def locked(self, user, anonymous_progress=None):
        """ Returns True if this segment is locked for a given user. """

        qs = self.get_prior_segments()

        if self.barrier == SegmentBarrierEnum.hard_barrier:
            ids = [s.id for s in qs]
            if not ids:
                return False

            if user:
                qs_progress = SegmentUserProgress.objects().filter(
                    SegmentUserProgress.user_id == user.id,
                    SegmentUserProgress.segment_id.in_(ids),
                    SegmentUserProgress.progress > SegmentStatusThreshold.completed,
                )
                return qs_progress.count() != len(ids)
            else:
                for key in ids:
                    if (
                        anonymous_progress.get(str(key), 0)
                        < SegmentStatusThreshold.completed
                    ):
                        return True

                return False
        elif self.barrier == SegmentBarrierEnum.paid:
            return not self.can_view(user)
        else:
            if user is None and self.barrier == SegmentBarrierEnum.login:
                return True

            barriers = list(qs.filter(self.barrier_filter(with_login=user is None)))
            return (
                not barriers[-1].can_view(user, anonymous_progress)
                if barriers
                else False
            )

    @classmethod
    def barrier_filter(cls, with_login=True):
        barriers = [
            SegmentBarrierEnum.hard_barrier,
            SegmentBarrierEnum.barrier,
            SegmentBarrierEnum.paid,
        ]
        if with_login:
            barriers.append(SegmentBarrierEnum.login)
        return cls.barrier.in_(barriers)

    @classmethod
    def filter_out_hidden(cls):
        return cls.barrier.in_(
            (
                SegmentBarrierEnum.hard_barrier,
                SegmentBarrierEnum.barrier,
                SegmentBarrierEnum.paid,
                SegmentBarrierEnum.login,
                SegmentBarrierEnum.normal,
                None,
            )
        )


class Segment(BarrierSegment, Survey, OrderedBase):
    __tablename__ = "lesson_segments"

    order_parent_name = "lesson"
    order_parent_key = "lesson_id"

    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.Enum(SegmentType), nullable=True)
    video_type = sa.Column(sa.Enum(VideoTypeEnum), nullable=True)
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)
    duration_seconds = sa.Column(sa.Integer)
    external_id = sa.Column(sa.String)
    url = sa.Column(sa.String)
    language = sa.Column(sa.String(2))
    slug = sa.Column(sa.String(50))  # Unique in relation to parent
    _thumbnail = sa.Column(sa.String)  # S3 Link

    lesson_id = sa.Column(sa.Integer, sa.ForeignKey("lessons.id"))
    lesson = orm.relationship("Lesson", back_populates="segments")

    translations = orm.relationship("SegmentTranslation", back_populates="segment")
    survey_answers = orm.relationship("SegmentSurveyResponse", back_populates="survey")

    __table_args__ = (
        sa.UniqueConstraint("lesson_id", "slug", name="_lesson_segment_uc"),
    )

    @property
    def duration(self):
        return self.duration_seconds

    @property
    def strfduration(self):
        return str(timedelta(seconds=self.duration_seconds))

    @property
    def template(self):
        if self.type == SegmentType.video:
            return "video_wistia"
        else:
            return self.type.name

    @property
    def permalink(self):
        return url_for(
            "course_display.view",
            segment_slug=self.slug,
            lesson_slug=self.lesson.slug,
            course_slug=self.lesson.course.slug,
        )

    @property
    def thumbnail(self):
        if not self._thumbnail and self.external_id:
            self._thumbnail = fetch_thumbnail_from_wistia(self.external_id)
            self.save()
        elif not self._thumbnail:
            return "http://placekitten.com/640/360"
        return self._thumbnail

    def set_duration(self):
        self.duration_seconds = 0
        if self.external_id and "wistia.com" in self.url:
            url = "http://fast.wistia.net/oembed?url=http://home.wistia.com/medias/{}?embedType=async&videoWidth=640".format(
                self.external_id
            )

            try:
                data = requests.get(url).json()
                self.duration_seconds = int(data["duration"])
            except (TypeError, ValueError, KeyError):
                if not self.duration_seconds:
                    self.duration_seconds = 0

    def user_progress(self, user, anonymous_progress=None):
        return SegmentUserProgress.user_progress(
            self.id, user.id if user else None, anonymous_progress
        )

    def save_user_progress(self, user, percent):
        return SegmentUserProgress.save_user_progress(self.id, user.id, percent)

    def find_user_progress(self, user_id):
        return SegmentUserProgress.find_user_progress(self.id, user_id)

    def first_child(self, child):
        return None

    def last_child(self, child):
        return None


class SegmentSurveyResponse(SurveyResponse):
    __tablename__ = "lesson_segments_survey_response"
    __table_args__ = (
        sa.UniqueConstraint(
            "segment_id", "user_id", name="_segment_survey_response_user_uc"
        ),
    )

    segment_id = sa.Column(sa.Integer, sa.ForeignKey("lesson_segments.id"))
    survey = orm.relationship("Segment", back_populates="survey_answers")
    user_id = sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"))
    user = orm.relationship("User", back_populates="segment_survey_answers")


class SegmentTranslation(Base):
    __tablename__ = "lesson_segments_translated"

    id = sa.Column(sa.Integer, primary_key=True)
    segment_id = sa.Column(sa.Integer, sa.ForeignKey("lesson_segments.id"))
    title = sa.Column(sa.String)
    duration_seconds = sa.Column(sa.Integer)
    url = sa.Column(sa.String)
    language = sa.Column(sa.String(2))

    segment = orm.relationship("Segment", back_populates="translations")
