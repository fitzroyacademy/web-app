from uuid import uuid4

from slugify import slugify
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from .base import BaseModel, get_session
from .enums import PreferenceTags

from .course import CourseEnrollment


class User(BaseModel):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(50), unique=True)
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True)
    phone_number = sa.Column(sa.String(15))
    dob = sa.Column(sa.Date)
    password_hash = sa.Column(sa.String(128))
    profile_picture = sa.Column(sa.String)
    bio = sa.Column(sa.String)
    super_admin = sa.Column(sa.Boolean, default=False)

    institutes = orm.relationship("InstituteEnrollment", back_populates="user")
    programs = orm.relationship("ProgramEnrollment", back_populates="user")
    course_enrollments = orm.relationship("CourseEnrollment", back_populates="user")

    @hybrid_property
    def password(self):
        return ""

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def available_username(cls, username):
        if cls.objects().filter(cls.username == username).first():
            username = username[:45] + "-" + str(uuid4())[:4]

        return slugify(username)

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def course_progress(self):
        courses = self.courses
        if len(courses) is 0:
            return 100
        total = 0
        for course in courses:
            total = total + course.user_progress(self)
        return int(total / len(courses))

    def set_preference(self, tag, boolean):
        UserPreference.set_preference(self, tag, boolean)

    def preference(self, tag):
        pref = UserPreference.get_preference(self, tag)
        return pref.toggled if pref is not None else False

    @property
    def courses(self):
        return CourseEnrollment.user_courses(self.id)

    def teaches(self, course):
        return CourseEnrollment.teaches(self.id, course.id)

    def enrolled(self, course):
        return CourseEnrollment.enrolled(self.id, course.id)

    @classmethod
    def find_by_email(cls, email):
        return cls.objects().filter(cls.email == email).first()


class UserPreference(BaseModel):
    __tablename__ = "users_preferences"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"))
    # Corresponds to PreferenceTags list for now.
    preference = sa.Column(sa.Integer)  # ToDo: replace with enum
    toggled = sa.Column(sa.Boolean)

    @classmethod
    def get_preference(cls, user, preference_tag):
        if preference_tag not in PreferenceTags:
            raise Exception("Preference Unknown: {}".format(preference_tag))
        i = PreferenceTags.index(preference_tag)
        return (
            cls.objects()
            .filter(UserPreference.user_id == user.id)
            .filter(UserPreference.preference == i)
            .first()
        )

    @classmethod
    def set_preference(cls, user, preference_tag, boolean):
        pref = cls.get_preference(user, preference_tag)
        session = get_session()
        if pref is None:
            i = PreferenceTags.index(preference_tag)
            pref = cls(user_id=user.id, preference=i, toggled=boolean)
        pref.toggled = boolean
        session.add(pref)
        session.commit()
