import json

import sqlalchemy as sa
from flask import session

from .base import BaseModel, get_session


class SegmentUserProgress(BaseModel):
    __tablename__ = "segment_user_progress"
    id = sa.Column(sa.Integer, primary_key=True)
    progress = sa.Column(sa.Integer)
    # No complex join definition for now.
    segment_id = sa.Column(sa.Integer, sa.ForeignKey("lesson_segments.id"))
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

    @classmethod
    def user_progress(cls, segment_id, user_id):
        if user_id is None:  # ToDo: remove this from models and move to request context
            anon_progress = json.loads(session.get("anon_progress", "{}"))
            return anon_progress.get(str(segment_id), 0)
        progress = cls.find_user_progress(segment_id, user_id)
        if progress:
            return progress.progress
        return 0

    @classmethod
    def find_user_progress(cls, segment_id, user_id):
        q = (
            cls.objects()
            .filter(cls.segment_id == segment_id)
            .filter(cls.user_id == user_id)
        )
        return q.first()

    @classmethod
    def save_user_progress(cls, segment_id, user_id, percent):
        session = get_session()
        user_progress = cls.find_user_progress(segment_id, user_id)
        percent = int(percent)
        if user_progress is None:
            user_progress = cls(
                segment_id=segment_id, user_id=user_id, progress=percent
            )
        elif user_progress.progress < percent:
            user_progress.progress = percent
        session.add(user_progress)
        session.commit()
        return user_progress
