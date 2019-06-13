from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as orm
import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash


Base = declarative_base()

class User(Base):

	__tablename__ = 'users'


	id = sa.Column(sa.Integer, primary_key=True)
	first_name = sa.Column(sa.String)
	last_name = sa.Column(sa.String)
	email = sa.Column(sa.String, unique=True)
	phone_number = sa.Column(sa.String(15))
	dob = sa.Column(sa.Date)
	password_hash = sa.Column(sa.String(128))

	institutes = orm.relationship("InstituteEnrollment", back_populates="user")
	programs = orm.relationship("ProgramEnrollment", back_populates="user")
	courses = orm.relationship("CourseEnrollment", back_populates="user")

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def to_json(self):
		return json.dumps(self, cls=AlchemyEncoder)


class Institute(Base):

	__tablename__ = 'institutes'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String)
	logo = sa.Column(sa.String)  # URL to picture resource

	users = orm.relationship("InstituteEnrollment", back_populates="institute")

	def add_user(self, user, access_level=0):
		association = InstituteEnrollment(access_level=access_level)
		association.institute = self
		association.user = user
		self.users.append(a)

	def to_json(self):
		return json.dumps(self, cls=AlchemyEncoder)


class InstituteEnrollment(Base):
	__tablename__ = 'users_institutes'

	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'))
	institute_id = sa.Column('institute_id', sa.Integer, sa.ForeignKey('institutes.id'))
	access_level = sa.Column('access_level', sa.Integer)

	user = orm.relationship("User", back_populates="institutes")
	institute = orm.relationship("Institute", back_populates="users")

	def to_json(self):
		return json.dumps(self, cls=AlchemyEncoder)


class Program(Base):

	__tablename__ = 'programs'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String)

	users = orm.relationship("ProgramEnrollment", back_populates="program")
	courses = orm.relationship("Course", back_populates="program")

	def add_user(self, user, access_level=0):
		association = ProgramEnrollment(access_level=access_level)
		association.program = self
		association.user = user
		self.users.append(a)

	def to_json(self):
		return json.dumps(self, cls=AlchemyEncoder)


class ProgramEnrollment(Base):
	__tablename__ = 'users_programs'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
	program_id = sa.Column(sa.Integer, sa.ForeignKey('programs.id'), primary_key=True)
	access_level = sa.Column(sa.Integer)

	user = orm.relationship("User", back_populates="programs")
	program = orm.relationship("Program", back_populates="users")


class Course(Base):

	__tablename__ = 'courses'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String)
	picture = sa.Column(sa.String)  # URL to picture resource
	cover_image = sa.Column(sa.String)
	slug = sa.Column(sa.String(50), unique=True)
	order = sa.Column(sa.Integer)
	year = sa.Column(sa.Date)
	course_code = sa.Column(sa.String(50))
	access_code = sa.Column(sa.String(16))
	paid = sa.Column(sa.Boolean)
	guest_access = sa.Column(sa.Boolean)

	program_id = sa.Column(sa.Integer, sa.ForeignKey('programs.id'))
	program = orm.relationship("Program", back_populates="courses")

	lessons = orm.relationship("Lesson", back_populates="course")

	users = orm.relationship("CourseEnrollment", back_populates="course")

	def add_user(self, user, access_level=0):
		association = CourseEnrollment(access_level=access_level)
		association.institute = self
		association.user = user
		self.users.append(a)

	def to_json(self):
		return json.dumps(self, cls=AlchemyEncoder)


class CourseEnrollment(Base):
	__tablename__ = 'users_courses'

	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'))
	course_id = sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'))
	access_level = sa.Column('access_level', sa.Integer)

	user = orm.relationship("User", back_populates="courses")
	course = orm.relationship("Course", back_populates="users")


class Lesson(Base):

	__tablename__ = 'lessons'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String)
	duration_seconds = sa.Column(sa.Integer) # derivable through children
	active = sa.Column(sa.Boolean)

	course_id = sa.Column(sa.Integer, sa.ForeignKey('courses.id'))
	course = orm.relationship("Course", back_populates="lessons")

	segments = orm.relationship("Segment", back_populates="lesson")
	resources = orm.relationship("Resource", back_populates="lesson")

	def to_json(self):
		return json.dumps(self, cls=AlchemyEncoder)


class Segment(Base):

	__tablename__ = 'lesson_segments'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String)
	duration_seconds = sa.Column(sa.Integer)
	external_id = sa.Column(sa.String)
	url = sa.Column(sa.String)
	language = sa.Column(sa.String(2))

	lesson_id = sa.Column(sa.Integer, sa.ForeignKey('lessons.id'))
	lesson = orm.relationship("Lesson", back_populates="segments")

	def to_json(self):
		return json.dumps(self, cls=AlchemyEncoder)


class Resource(Base):

	__tablename__ = 'lesson_resources'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String)
	url = sa.Column(sa.String)
	type = sa.Column(sa.String)
	language = sa.Column(sa.String(2))
	featured = sa.Column(sa.Boolean)

	lesson_id = sa.Column(sa.Integer, sa.ForeignKey('lessons.id'))
	lesson = orm.relationship("Lesson", back_populates="resources")

	def to_json(self):
		return json.dumps(self, cls=AlchemyEncoder)


engine = sa.create_engine('sqlite:///dev_db.sqlite')
Base.metadata.create_all(engine)
