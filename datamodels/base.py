from os import environ

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.exc import IntegrityError
from wtforms.validators import ValidationError

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
        # ToDo: add objects manager
        session = get_session()
        return session.query(cls).filter(cls._is_deleted == deleted)

    def __getattr__(self, item):
        """
        This method causes problems while debugging. If you get exception
        AttributeError: 'super' object has no attribute '__getattr__'
        look for attribute name that doesn't exist in a class, which might be different from "item"
        but it's either "item" or an attribute inside method/property "item".
        """
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

    def save(self):
        try:
            db_session = get_session()
            db_session.add(self)
            db_session.commit()
        except IntegrityError:
            raise ValidationError("Invalid data.")

    @classmethod
    def _query(cls, **kwargs):
        db_session = get_session()
        q = db_session.query(cls).filter_by(_is_deleted=False).filter_by(**kwargs)
        return q

    @classmethod
    def first(cls, **kwargs):
        return cls._query(**kwargs).first()

    def delete(self, hard=False):
        if hard:
            db_session = get_session()
            db_session.delete(self)
            db_session.commit()
        else:
            self._is_deleted = True
            self.save()

    @classmethod
    def paginated_list(cls, page=1, page_size=None, order_by=None, desc=False):
        if page_size is None:
            page_size = app.config.get("PAGE_SIZE", 10)
        db_session = get_session()
        q = db_session.query(cls)
        if order_by is not None:
            if desc is True:
                order = sa.desc(order_by)
            else:
                order = order_by
            q = q.order_by(order)
        return q.limit(page_size).offset(page_size * (page - 1)).all()


class OrderedBase(BaseModel):
    __abstract__ = True
    order_parent_name = ""
    order_parent_key = ""

    order = sa.Column(sa.Integer)

    @classmethod
    def get_ordered_items(cls):
        return cls.objects().filter(cls.order >= 0).order_by(cls.order)

    @classmethod
    def ordered_items_for_parent(cls, parent, key="", desc=False):
        key = key or cls.order_parent_key
        if desc:
            ordered_by = sa.desc(cls.order)
        else:
            ordered_by = cls.order
        return cls.objects().filter(getattr(cls, key) == parent.id).order_by(ordered_by)

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

    @property
    def previous(self):
        parent = self.get_parent()
        items = self.ordered_items_for_parent(parent, key=self.order_parent_key).all()
        i = items.index(self)
        previous_parent = (
            parent.previous if parent and self.is_parent_ordered(parent) else None
        )
        if i == 0 and previous_parent is None:
            return None
        elif i == 0 and previous_parent is not None:
            return previous_parent.last_child(self)
        else:
            return items[i - 1]

    @property
    def next(self):
        parent = self.get_parent()
        if parent:
            items = self.ordered_items_for_parent(
                parent=parent, key=self.order_parent_key
            ).all()
        else:
            items = self.get_ordered_items().all()

        i = items.index(self)
        next_parent = parent.next if parent and self.is_parent_ordered(parent) else None
        if i == len(items) - 1 and next_parent is None:
            return None
        elif i == len(items) - 1 and next_parent is not None:
            return next_parent.first_child(self)
        return items[i + 1]

    def last_child(self, child):
        """
        Should be implemented only for classes that acts as parents for ordered children
        """
        raise NotImplementedError

    def first_child(self, child):
        """
        Should be implemented only for classes that acts as parents for ordered children
        """
        raise NotImplementedError

    def get_parent(self):
        return getattr(self, self.order_parent_name) if self.order_parent_name else None

    @staticmethod
    def is_parent_ordered(parent):
        return hasattr(parent, "order_parent_key") if parent else False
