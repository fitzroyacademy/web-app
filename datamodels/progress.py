import sqlalchemy as sa

from datamodels.base import BaseModel


class SegmentUserProgress(BaseModel):
    __tablename__ = "segment_user_progress"
    id = sa.Column(sa.Integer, primary_key=True)
    progress = sa.Column(sa.Integer)
    # No complex join definition for now.
    segment_id = sa.Column(sa.Integer, sa.ForeignKey("lesson_segments.id"))
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

    @classmethod
    def user_progress(cls, segment_id, user_id, anonymous_progress=None):
        if anonymous_progress is None or not isinstance(anonymous_progress, dict):
            anonymous_progress = {}
        if user_id is None:
            return anonymous_progress.get(str(segment_id), 0)
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

        user_progress = cls.find_user_progress(segment_id, user_id)
        percent = int(percent)
        if user_progress is None:
            user_progress = SegmentUserProgress(
                segment_id=segment_id, user_id=user_id, progress=percent
            )
        elif user_progress.progress < percent:
            user_progress.progress = percent
        user_progress.save()
        return user_progress
