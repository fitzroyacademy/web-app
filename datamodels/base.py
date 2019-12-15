from os import environ

import sqlalchemy as sa
import sqlalchemy.orm as orm

from flask import current_app as app
from flask import url_for
from sqlalchemy.ext.declarative import declarative_base

_session = None


def get_session():
    global _session
    if _session is None:
        engine = sa.create_engine(app.config["DB_URI"])
        Base.metadata.create_all(engine)
        Session = orm.scoped_session(orm.sessionmaker(bind=engine))
        _session = Session()
    return _session


def _clear_session_for_tests():
    global _session
    if "FLASK_ENV" not in environ or environ["FLASK_ENV"] != "test":
        raise Exception("Session clearing is for test instances only.")
    _session = None


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    _is_deleted = sa.Column(sa.Boolean, default=False)

    @classmethod
    def find_by_id(cls, obj_id):
        return cls.objects().filter(cls.id == obj_id).first()

    @classmethod
    def find_by_slug(cls, slug):
        if hasattr(cls, "slug"):
            return cls.objects().filter(cls.slug == slug).first()
        else:
            raise AttributeError("Object do not has attribute slug")

    @classmethod
    def objects(cls, deleted=False):
        session = get_session()
        return session.query(cls).filter(cls._is_deleted == deleted)

    def __getattr__(self, item):
        if item.endswith("_url"):
            return self._image_field_url(item[:-4])

        return super().__getattr__(item)

    def _image_field_url(self, field):
        image_field = getattr(self, field, None)
        if not image_field:
            return ""
        if image_field.startswith("/static/"):
            return image_field
        return (
            url_for("static", filename="uploads/{}".format(image_field))
            if image_field and not image_field.startswith("http")
            else image_field
        )


class OrderedBase(BaseModel):
    __abstract__ = True

    order = sa.Column(sa.Integer)

    @classmethod
    def get_ordered_items(cls):
        return cls.objects().filter(cls.order >= 0).order_by(cls.order)

    @classmethod
    def ordered_items_for_parent(cls, parent, key):
        return cls.objects().filter(getattr(cls, key) == parent.id).order_by(cls.order)

    @classmethod
    def reorder_items(cls, items_order):
        lessons_mapping = [
            {"id": items_order[i], "order": i + 1} for i in range(len(items_order))
        ]
        db = get_session()
        db.bulk_update_mappings(cls, lessons_mapping)
        db.commit()

    @classmethod
    def delete(cls, instance, parent=None, key=None):
        if parent:
            session = get_session()
            session.delete(instance)
            session.commit()

            list_of_items = [
                l.id
                for l in cls.objects()
                .filter(getattr(cls, key) == parent.id)
                .order_by(cls.order)
            ]
            if list_of_items:
                cls.reorder_items(list_of_items)
