from datetime import timedelta

import requests
import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask import url_for

from .base import OrderedBase, Base
from .enums import (
    VideoTypeEnum,
    SegmentBarrierEnum,
    SegmentStatus,
    SegmentStatusThreshold,
)

from utils.images import fetch_thumbnail_from_wistia
from .progress import SegmentUserProgress


class BarrierSegment(Base):
    __abstract__ = True
    barrier = sa.Column(sa.Enum(SegmentBarrierEnum), nullable=True)
    user = None

    def can_view(self):
        return self.__can_view_dispatcher()

    def is_hidden_segment(self):
        return self.barrier == SegmentBarrierEnum.hidden

    def __can_view_dispatcher(self):
        perm_name = self.barrier.name
        handler = getattr(self, "_can_view_{}".format(perm_name), None)

        if handler is None:
            # Make sure that when new barrier type is added then there is a handler
            raise NotImplementedError(
                "Dispatcher for permission {} not implemented".format(perm_name)
            )

        return handler()

    def _can_view_normal(self):
        return True

    def _can_view_paid(self):
        return False

    def _can_view_login(self):
        return self.user is not None

    def _can_view_barrier(self):
        return self.user_status(self.user) == "completed"

    def _can_view_hard_barrier(self):
        return self.user_status(self.user) == "completed"

    def _can_view_hidden(self):
        return self.user.teaches(self.lesson.course)

    def user_status(self, user, progress=None):

        if self.locked(user):
            return SegmentStatus.locked

        p = progress or self.user_progress(user)
        if p > SegmentStatusThreshold.completed:
            return SegmentStatus.completed
        if p > SegmentStatusThreshold.touched:
            return SegmentStatus.touched
        return SegmentStatus.accessible

    def locked(self, user, anonymous_progress=None):
        """ Returns True if this segment is locked for a given user. """

        if anonymous_progress is None:
            anonymous_progress = {}

        qs = self.lesson.course.get_ordered_segments().filter(
            sa.or_(
                sa.and_(
                    self.lesson.__class__.order == self.lesson.order,
                    Segment.order < self.order,
                ),
                self.lesson.__class__.order < self.lesson.order,
            )
        )

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

        else:
            qs = qs.filter(self.barrier_filter())

            barriers = list(qs)
            return (
                barriers[-1].user_progress(user) < SegmentStatusThreshold.completed
                if barriers and barriers[-1].barrier != SegmentBarrierEnum.login
                else False
            )

    @classmethod
    def barrier_filter(cls):
        return cls.barrier.in_(
            (
                SegmentBarrierEnum.hard_barrier,
                SegmentBarrierEnum.barrier,
                SegmentBarrierEnum.paid,
                SegmentBarrierEnum.login,
            )
        )

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


class Segment(BarrierSegment, OrderedBase):
    __tablename__ = "lesson_segments"

    order_parent_name = "lesson"
    order_parent_key = "lesson_id"

    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.String)
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

    __table_args__ = (
        sa.UniqueConstraint("lesson_id", "slug", name="_lesson_sement_uc"),
    )

    @property
    def duration(self):
        return self.duration_seconds

    @property
    def strfduration(self):
        return str(timedelta(seconds=self.duration_seconds))

    @property
    def template(self):
        return "video_wistia"

    @property
    def permalink(self):
        return url_for(
            "segment.view",
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

    def user_progress(self, user):
        return SegmentUserProgress.user_progress(self.id, user.id if user else None)

    def save_user_progress(self, user, percent):
        return SegmentUserProgress.save_user_progress(self.id, user.id, percent)

    def find_user_progress(self, user_id):
        return SegmentUserProgress.find_user_progress(self.id, user_id)

    def first_child(self, child):
        return None

    def last_child(self, child):
        return None


class SegmentTranslation(Base):
    __tablename__ = "lesson_segments_translated"

    id = sa.Column(sa.Integer, primary_key=True)
    segment_id = sa.Column(sa.Integer, sa.ForeignKey("lesson_segments.id"))
    title = sa.Column(sa.String)
    duration_seconds = sa.Column(sa.Integer)
    url = sa.Column(sa.String)
    language = sa.Column(sa.String(2))

    segment = orm.relationship("Segment", back_populates="translations")
