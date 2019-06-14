from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as orm
import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash
import json


Base = declarative_base()

def dump(obj, seen=None):
	if not isinstance(obj, Base):
		return obj
	seen = seen or []  # Recursion trap.
	seen.append(id(obj))
	ignored = ["metadata"]
	fields = {}
	for f in [x for x in dir(obj) if x.startswith('_') is False and x not in ignored]:
		data = getattr(obj, f)
		try:
			json.dumps(data)
			fields[f] = data
		except TypeError:
			if isinstance(data, Base):
				if id(data) in seen:
					fields[f] = None
				else:
					fields[f] = dump(data, seen)
			elif callable(data) and f.startswith('get_'):
					fields[f[4:]] = dump(data(), seen)
			elif isinstance(data, list):
				fields[f] = []
				for o in data:
					if id(o) in seen:
						fields[f].append(None)
					else:
						fields[f].append(dump(o, seen))
	return fields


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


class Institute(Base):

	__tablename__ = 'institutes'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String)
	logo = sa.Column(sa.String)  # URL to picture resource
	slug = sa.Column(sa.String(50), unique=True)

	users = orm.relationship("InstituteEnrollment", back_populates="institute")

	def add_user(self, user, access_level=0):
		association = InstituteEnrollment(access_level=access_level)
		association.institute = self
		association.user = user
		self.users.append(a)


class InstituteEnrollment(Base):
	__tablename__ = 'users_institutes'

	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'))
	institute_id = sa.Column('institute_id', sa.Integer, sa.ForeignKey('institutes.id'))
	access_level = sa.Column('access_level', sa.Integer)

	user = orm.relationship("User", back_populates="institutes")
	institute = orm.relationship("Institute", back_populates="users")


class Program(Base):

	__tablename__ = 'programs'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String)
	slug = sa.Column(sa.String(50), unique=True)

	users = orm.relationship("ProgramEnrollment", back_populates="program")
	courses = orm.relationship("Course", back_populates="program")

	def add_user(self, user, access_level=0):
		association = ProgramEnrollment(access_level=access_level)
		association.program = self
		association.user = user
		self.users.append(a)


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
	order = sa.Column(sa.Integer)
	year = sa.Column(sa.Date)
	course_code = sa.Column(sa.String(50))
	access_code = sa.Column(sa.String(16))
	paid = sa.Column(sa.Boolean)
	guest_access = sa.Column(sa.Boolean)
	language = sa.Column(sa.String(2))
	slug = sa.Column(sa.String(50), unique=True)

	program_id = sa.Column(sa.Integer, sa.ForeignKey('programs.id'))
	program = orm.relationship("Program", back_populates="courses")

	lessons = orm.relationship("Lesson", back_populates="course")

	users = orm.relationship("CourseEnrollment", back_populates="course")
	translations = orm.relationship("CourseTranslation", back_populates="course")

	def add_user(self, user, access_level=0):
		association = CourseEnrollment(access_level=access_level)
		association.institute = self
		association.user = user
		self.users.append(a)


class CourseTranslation(Base):

	__tablename__ = 'courses_translated'

	id = sa.Column(sa.Integer, primary_key=True)
	course_id = sa.Column(sa.Integer, sa.ForeignKey('courses.id'))
	title = sa.Column(sa.String)
	language = sa.Column(sa.String(2))

	course = orm.relationship("Course", back_populates="translations")


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
	language = sa.Column(sa.String(2))
	slug = sa.Column(sa.String(50))  # Unique in relation to parent
	order = sa.Column(sa.Integer)

	course_id = sa.Column(sa.Integer, sa.ForeignKey('courses.id'))
	course = orm.relationship("Course", back_populates="lessons")

	segments = orm.relationship("Segment", back_populates="lesson")
	resources = orm.relationship("Resource", back_populates="lesson")

	translations = orm.relationship("LessonTranslation", back_populates="lesson")

	@orm.validates('slug')
	def validate_slug(self, key, value):
		""" Check the parent course for any duplicate lesson slugs """
		pass


class LessonTranslation(Base):

	__tablename__ = 'lessons_translated'

	id = sa.Column(sa.Integer, primary_key=True)
	lesson_id = sa.Column(sa.Integer, sa.ForeignKey('lessons.id'))
	title = sa.Column(sa.String)
	duration_seconds = sa.Column(sa.Integer)
	url = sa.Column(sa.String)
	language = sa.Column(sa.String(2))

	lesson = orm.relationship("Lesson", back_populates="translations")


class Segment(Base):

	__tablename__ = 'lesson_segments'

	id = sa.Column(sa.Integer, primary_key=True)
	type = sa.Column(sa.String)
	title = sa.Column(sa.String)
	duration_seconds = sa.Column(sa.Integer)
	external_id = sa.Column(sa.String)
	url = sa.Column(sa.String)
	language = sa.Column(sa.String(2))
	slug = sa.Column(sa.String(50))  # Unique in relation to parent
	order = sa.Column(sa.Integer)

	lesson_id = sa.Column(sa.Integer, sa.ForeignKey('lessons.id'))
	lesson = orm.relationship("Lesson", back_populates="segments")

	translations = orm.relationship("SegmentTranslation", back_populates="segment")

	@orm.validates('slug')
	def validate_slug(self, key, value):
		""" Check the parent lesson for any duplicate segment slugs """
		pass


class SegmentTranslation(Base):

	__tablename__ = 'lesson_segments_translated'

	id = sa.Column(sa.Integer, primary_key=True)
	segment_id = sa.Column(sa.Integer, sa.ForeignKey('lesson_segments.id'))
	title = sa.Column(sa.String)
	duration_seconds = sa.Column(sa.Integer)
	url = sa.Column(sa.String)
	language = sa.Column(sa.String(2))

	segment = orm.relationship("Segment", back_populates="translations")


class Resource(Base):

	__tablename__ = 'lesson_resources'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String)
	url = sa.Column(sa.String)
	type = sa.Column(sa.String)
	order = sa.Column(sa.Integer)
	featured = sa.Column(sa.Boolean)

	lesson_id = sa.Column(sa.Integer, sa.ForeignKey('lessons.id'))
	lesson = orm.relationship("Lesson", back_populates="resources")

	translations = orm.relationship("ResourceTranslation", back_populates="resource")


class ResourceTranslation(Base):

	__tablename__ = 'lesson_resources_translated'

	id = sa.Column(sa.Integer, primary_key=True)
	resource_id = sa.Column(sa.Integer, sa.ForeignKey('lesson_resources.id'))
	title = sa.Column(sa.String)
	url = sa.Column(sa.String)
	language = sa.Column(sa.String(2))

	resource = orm.relationship("Resource", back_populates="translations")


_session = None
def get_session():
	global _session
	if _session is None:
		engine = sa.create_engine('sqlite:///dev_db.sqlite')
		Base.metadata.create_all(engine)
		Session = orm.sessionmaker(bind=engine)
		_session = Session()
	return _session


def get_course_by_slug(slug):
	session = get_session()
	return session.query(Course).filter(Course.slug == slug).one()

def get_lesson_by_slug(course_slug, lesson_slug):
	session = get_session()
	q = session.query(Lesson).\
		join(Lesson.course).\
		filter(Course.slug == course_slug).\
		filter(Lesson.slug == lesson_slug)
	try:
		return q.one()
	except:
		return None

def get_segment_by_slug(course_slug, lesson_slug, segment_slug):
	session = get_session()
	q = session.query(Segment).\
		join(Lesson.segments).\
		join(Lesson.course).\
		filter(Course.slug == course_slug).\
		filter(Lesson.slug == lesson_slug).\
		filter(Segment.slug == segment_slug)
	try:
		return q.one()
	except:
		return None
