import sqlalchemy as sa
import sqlalchemy.orm as orm

from .base import BaseModel, get_session
from .custom_settings_list import CUSTOM_SETTINGS_KEYS


class CustomSetting(BaseModel):
    __tablename__ = "custom_setting"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "key", name="_course_user_enrollment"),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    key = sa.Column(sa.String(16))
    value = sa.Column(sa.String(64))
    user_id = sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"))
    user = orm.relationship("User", back_populates="custom_settings")

    @classmethod
    def set_setting(cls, key, value, user):
        obj = cls.get_setting(key, user)

        if key not in CUSTOM_SETTINGS_KEYS:
            raise ValueError("There is no such key")

        if obj is None:
            obj = CustomSetting(key=key, value=value, user=user)
        else:
            obj.value = value
        s = get_session()
        s.add(obj)
        s.commit()

        return obj

    @classmethod
    def get_setting(cls, key, user):
        return cls.objects().filter(cls.user == user, cls.key == key).first()
