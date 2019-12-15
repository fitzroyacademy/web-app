import sqlalchemy as sa
import sqlalchemy.orm as orm

from .base import BaseModel, get_session
from .enums import InstitutePermissionEnum


class Institute(BaseModel):
    __tablename__ = "institutes"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String(140), default="")
    cover_image = sa.Column(sa.String, default="")
    logo = sa.Column(sa.String, default="")  # URL to picture resource
    slug = sa.Column(sa.String(50), unique=True)  # corresponds to subdomain
    for_who = sa.Column(sa.String, default="")
    location = sa.Column(sa.String, default="")

    users = orm.relationship("InstituteEnrollment", back_populates="institute")
    courses = orm.relationship("Course", back_populates="institute")

    def add_user(self, user, access_level=InstitutePermissionEnum.teacher):
        association = InstituteEnrollment(
            institute=self, access_level=access_level, user=user
        )
        db = get_session()
        self.users.append(association)
        db.commit()

    def add_manager(self, user):
        self.add_user(user, access_level=InstitutePermissionEnum.manager)

    def add_admin(self, user):
        self.add_user(user, access_level=InstitutePermissionEnum.admin)

    def _get_user_group(self, group_name):
        associations = getattr(
            InstituteEnrollment, "find_{}_for_institute".format(group_name)
        )(self.id)
        users = []
        for ass in associations:
            users.append(ass.user)
        return users

    @property
    def teachers(self):
        """ A unique list of users associated with this course that
        have teacher-level access."""
        return self._get_user_group("teachers")

    @property
    def admins(self):
        return self._get_user_group("admins")

    @property
    def managers(self):
        return self._get_user_group("managers")

    def is_admin(self, user):
        return InstituteEnrollment.is_admin(self.id, user.id)

    def remove_user(self, user, access_level):
        access_level = getattr(InstitutePermissionEnum, access_level, None)

        if access_level is None:
            return False

        enrollment = (
            InstituteEnrollment.filter_by_institute_user(self.id, user.id)
            .filter(InstituteEnrollment.access_level == access_level)
            .first()
        )

        if enrollment:
            s = get_session()
            s.delete(enrollment)
            s.commit()
            return True
        return False


class InstituteEnrollment(BaseModel):
    __tablename__ = "users_institutes"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"))
    institute_id = sa.Column("institute_id", sa.Integer, sa.ForeignKey("institutes.id"))
    access_level = sa.Column(sa.Enum(InstitutePermissionEnum), nullable=True)

    user = orm.relationship("User", back_populates="institutes")
    institute = orm.relationship("Institute", back_populates="users")

    @classmethod
    def find_users_for_institute(cls, institute_id, access_level):
        session = get_session()
        return (
            session.query(cls)
            .filter(cls.institute_id == institute_id)
            .filter(cls.access_level == access_level)
            .all()
        )

    @classmethod
    def filter_by_institute_user(cls, institute_id, user_id):
        session = get_session()
        return (
            session.query(cls)
            .filter(cls.institute_id == institute_id)
            .filter(cls.user_id == user_id)
        )

    @classmethod
    def is_admin(cls, institute_id, user_id):
        return (
            cls.filter_by_institute_user(institute_id, user_id)
            .filter(cls.access_level == InstitutePermissionEnum.admin)
            .first()
            is not None
        )

    @classmethod
    def find_admins_for_institute(
        cls, institute_id, access_level=InstitutePermissionEnum.admin
    ):
        return cls.find_users_for_institute(institute_id, access_level)

    @classmethod
    def find_teachers_for_institute(
        cls, institute_id, access_level=InstitutePermissionEnum.teacher
    ):
        return cls.find_users_for_institute(institute_id, access_level)

    @classmethod
    def find_managers_for_institute(
        cls, institute_id, access_level=InstitutePermissionEnum.manager
    ):
        return cls.find_users_for_institute(institute_id, access_level)


class Program(BaseModel):
    __tablename__ = "programs"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    slug = sa.Column(sa.String(50), unique=True)

    users = orm.relationship("ProgramEnrollment", back_populates="program")
    courses = orm.relationship("Course", back_populates="program")

    def add_user(self, user, access_level=0):
        association = ProgramEnrollment(access_level=access_level)
        association.program = self
        association.user = user
        self.users.append(association)


class ProgramEnrollment(BaseModel):
    __tablename__ = "users_programs"

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True)
    program_id = sa.Column(sa.Integer, sa.ForeignKey("programs.id"), primary_key=True)
    access_level = sa.Column(sa.Integer)

    user = orm.relationship("User", back_populates="programs")
    program = orm.relationship("Program", back_populates="users")


def get_program_by_slug(slug):
    return Program.find_by_slug(slug)
