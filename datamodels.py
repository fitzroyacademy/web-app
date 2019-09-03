from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as orm
import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash
import json
from os import environ
from sqlalchemy.ext.hybrid import hybrid_property
from flask import current_app as app
from flask import url_for
import pprint
import requests
from datetime import datetime

Base = declarative_base()

def dump(obj, seen=None):
	if not isinstance(obj, Base):
		if isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], Base):
			o = []
			for i in obj:
				o.append(dump(i, seen=seen))
			return o
		else:
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
	username = sa.Column(sa.String(50), unique=True)
	first_name = sa.Column(sa.String)
	last_name = sa.Column(sa.String)
	email = sa.Column(sa.String, unique=True)
	phone_number = sa.Column(sa.String(15))
	dob = sa.Column(sa.Date)
	password_hash = sa.Column(sa.String(128))
	profile_picture = sa.Column(sa.String)
	bio = sa.Column(sa.String)

	institutes = orm.relationship("InstituteEnrollment", back_populates="user")
	programs = orm.relationship("ProgramEnrollment", back_populates="user")
	course_enrollments = orm.relationship("CourseEnrollment", back_populates="user")

	@hybrid_property
	def password(self):
		return ''

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	@property
	def full_name(self):
		return " ".join([self.first_name, self.last_name])

	@property
	def courses(self):
		courses = []
		for enrollment in CourseEnrollment.find_by_user(self.id):
			courses.append(enrollment.course)
		return courses

	def set_preference(self, tag, boolean):
		UserPreference.set_preference(self, tag, boolean)

	def preference(self, tag):
		pref = UserPreference.get_preference(self, tag)
		if pref is not None:
			return pref.toggled
		return False

	def merge_anonymous_data(self, data):
		for seg_id in data:
			save_segment_progress(seg_id, self.id, int(data[seg_id]))

	def teaches(self, course):
		e = CourseEnrollment.find_by_course_and_student(course.id, self.id)
		if e is None:
			return False
		if e.access_level == COURSE_ACCESS_TEACHER:
			return True
		return False

	@staticmethod
	def find_by_id(user_id):
		session = get_session()
		return session.query(User).filter(User.id == user_id).first()

	@staticmethod
	def find_by_email(email):
		session = get_session()
		return session.query(User).filter(User.email == email).first()


PreferenceTags = [
	'emails_from_teachers',
	'emails_from_site',
	'data_research',
	'data_show_name',
	'data_show_email'
]

class UserPreference(Base):

	__tablename__ = 'users_preferences'

	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'))
	# Corresponds to PreferenceTags list for now.
	preference = sa.Column(sa.Integer)
	toggled = sa.Column(sa.Boolean)

	@staticmethod
	def get_preference(user, preference_tag):
		if preference_tag not in PreferenceTags:
			raise Exception("Preference Unknown: {}".format(preference_tag))
		i = PreferenceTags.index(preference_tag)
		session = get_session()
		return session.query(UserPreference).\
		    filter(UserPreference.user_id == user.id).\
		    filter(UserPreference.preference == i).\
		    first()

	@staticmethod
	def set_preference(user, preference_tag, boolean):
		pref = UserPreference.get_preference(user, preference_tag)
		if pref is None:
			i = PreferenceTags.index(preference_tag)
			session = get_session()
			pref = UserPreference(user_id = user.id, preference=i, toggled=boolean)
		pref.boolean = boolean
		session.add(pref)
		session.commit()

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
		self.users.append(association)

	@staticmethod
	def find_by_slug(slug):
		session = get_session()
		return session.query(Institute).filter(Institute.slug == slug).first()


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
		self.users.append(association)

	@classmethod
	def find_by_slug(cls, slug):
		session = get_session()
		return session.query(cls).filter(cls.slug == slug).first()


class ProgramEnrollment(Base):
	__tablename__ = 'users_programs'

	user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
	program_id = sa.Column(sa.Integer, sa.ForeignKey('programs.id'), primary_key=True)
	access_level = sa.Column(sa.Integer)

	user = orm.relationship("User", back_populates="programs")
	program = orm.relationship("Program", back_populates="users")


COURSE_ACCESS_STUDENT = 1
COURSE_ACCESS_TEACHER = 2
COURSE_ACCESS_ADMIN = 3

class Course(Base):

	__tablename__ = 'courses'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String)
	picture = sa.Column(sa.String)  # URL to picture resource
	cover_image = sa.Column(sa.String)
	order = sa.Column(sa.Integer)
	year = sa.Column(sa.Date)
	course_code = sa.Column(sa.String(16), unique=True)
	paid = sa.Column(sa.Boolean)
	guest_access = sa.Column(sa.Boolean)
	language = sa.Column(sa.String(2))
	slug = sa.Column(sa.String(50), unique=True)
	draft = sa.Column(sa.Boolean, default=True)

	target_audience = sa.Column(sa.String())
	skill_level = sa.Column(sa.String())
	info = sa.Column(sa.String)

	summary_html = sa.Column(sa.String())

	program_id = sa.Column(sa.Integer, sa.ForeignKey('programs.id'))
	program = orm.relationship("Program", back_populates="courses")

	lessons = orm.relationship("Lesson", back_populates="course")

	users = orm.relationship("CourseEnrollment", back_populates="course")
	translations = orm.relationship("CourseTranslation", back_populates="course")

	preview_thumbnail = sa.Column(sa.String)

	def add_user(self, user, access_level=0):
		association = CourseEnrollment(access_level=access_level)
		association.course = self
		association.user = user
		self.users.append(association)

	def add_instructor(self, user):
		self.add_user(user, COURSE_ACCESS_TEACHER)

	@property
	def duration_seconds(self):
		t = 0
		for lesson in self.lessons:
			t += lesson.duration_seconds
		return t

	@property
	def permalink(self):
		return url_for('course.view', slug=self.slug)

	@property
	def thumbnail(self):
		return self.lessons[0].thumbnail

	@property
	def instructors(self):
		""" A unique list of users associated with this course that
		have teacher-level access."""
		associations = CourseEnrollment.find_teachers_for_course(self.id)
		users = []
		for ass in associations:
			users.append(ass.user)
		return users

	def enroll(self, student):
		""" Adds a user to a course with student-level access. """
		if get_enrollment(self.id, student.id) is None:
			enrollment = CourseEnrollment(
				course_id=self.id, user_id=student.id,
				access_level=COURSE_ACCESS_STUDENT
			)
			s = get_session()
			s.add(enrollment)
			s.commit()

	@staticmethod
	def find_by_slug(slug):
		session = get_session()
		return session.query(Course).filter(Course.slug == slug).first()

	@staticmethod
	def find_by_code(code):
		session = get_session()
		return session.query(Course).filter(Course.course_code == code).first()


class CourseTranslation(Base):

	__tablename__ = 'courses_translated'

	id = sa.Column(sa.Integer, primary_key=True)
	course_id = sa.Column(sa.Integer, sa.ForeignKey('courses.id'))
	title = sa.Column(sa.String)
	language = sa.Column(sa.String(2))

	course = orm.relationship("Course", back_populates="translations")


class CourseEnrollment(Base):
	__tablename__ = 'users_courses'
	__table_args__ = (sa.UniqueConstraint('course_id', 'user_id', name='_course_user_enrollment'),)

	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'))
	course_id = sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id'))
	access_level = sa.Column('access_level', sa.Integer)

	user = orm.relationship("User", back_populates="course_enrollments")
	course = orm.relationship("Course", back_populates="users")

	@staticmethod
	def find_by_course_and_student(course_id, student_id):
		session = get_session()
		return session.query(CourseEnrollment).filter(
			CourseEnrollment.course_id == course_id)\
		.filter(
			CourseEnrollment.user_id == student_id
		).first()

	@staticmethod
	def find_teachers_for_course(course_id):
		session = get_session()
		return session.query(CourseEnrollment).filter(
			CourseEnrollment.course_id == course_id)\
		.filter(
			CourseEnrollment.access_level == COURSE_ACCESS_TEACHER
		).all()

	@staticmethod
	def find_by_user(user_id):
		session = get_session()
		return session.query(CourseEnrollment).filter(
			CourseEnrollment.user_id == user_id
		).all()

class Lesson(Base):

	__tablename__ = 'lessons'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String)
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
		""" TODO: Check the parent course for any duplicate lesson slugs """
		return value

	@property
	def permalink(self):
		return url_for(
			'lesson.view',
			course_slug=self.course.slug,
			lesson_slug=self.slug
		)

	@property
	def thumbnail(self):
		return self.segments[0].thumbnail

	@property
	def duration_seconds(self):
		t = 0
		for seg in self.segments:
			t += seg.duration_seconds
		return t

	@staticmethod
	def find_by_id(lesson_id):
		session = get_session()
		return session.query(Lesson).filter(Lesson.id == lesson_id).first()

	@staticmethod
	def find_by_slug(course_slug, lesson_slug):
		session = get_session()
		q = session.query(Lesson).\
			join(Lesson.course).\
			filter(Course.slug == course_slug).\
			filter(Lesson.slug == lesson_slug)
		try:
			return q.first()
		except:
			return None


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
	_thumbnail = sa.Column(sa.String)  # S3 Link

	lesson_id = sa.Column(sa.Integer, sa.ForeignKey('lessons.id'))
	lesson = orm.relationship("Lesson", back_populates="segments")

	translations = orm.relationship("SegmentTranslation", back_populates="segment")

	@orm.validates('slug')
	def validate_slug(self, key, value):
		""" TODO: Check the parent lesson for any duplicate segment slugs """
		return value

	@property
	def duration(self):
		return self.duration_seconds

	@property
	def template(self):
		return "video_wistia"

	@property
	def permalink(self):
		return url_for(
			"segment.view",
			segment_slug=self.slug,
			lesson_slug=self.lesson.slug,
			course_slug=self.lesson.course.slug
		)

	@property
	def thumbnail(self):
		if self._thumbnail is None:
			self._thumbnail = fetch_thumbnail(self.external_id)
			return "http://placekitten.com/640/360"
		return self._thumbnail

	def user_progress(self, user):
		if user is None:
			return 0
		progress = get_segment_progress(self.id, user.id)
		if progress:
			return progress.progress
		return 0

	def save_user_progress(self, user, percent):
		return save_segment_progress(self.id, user.id, percent)

	@staticmethod
	def find_by_id(segment_id):
		session = get_session()
		return session.query(Segment).filter(Segment.id == segment_id).first()

	@staticmethod
	def find_user_progress(segment_id, user_id):
		session = get_session()
		q = session.query(SegmentUserProgress).\
			filter(SegmentUserProgress.segment_id == segment_id).\
			filter(SegmentUserProgress.user_id == user_id)
		try:
			return q.first()
		except:
			return None

	@staticmethod
	def find_by_slug(course_slug, lesson_slug, segment_slug):
		session = get_session()
		q = session.query(Segment).\
			join(Lesson.segments).\
			join(Lesson.course).\
			filter(Course.slug == course_slug).\
			filter(Lesson.slug == lesson_slug).\
			filter(Segment.slug == segment_slug)
		try:
			return q.first()
		except:
			return None


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
	language = sa.Column(sa.String(2))
	slug = sa.Column(sa.String(50))
	anonymous_views = sa.Column(sa.Integer, default=0)

	lesson_id = sa.Column(sa.Integer, sa.ForeignKey('lessons.id'))
	lesson = orm.relationship("Lesson", back_populates="resources")

	@property
	def total_views(self):
		return LessonResourceUserAccess.count_access(self.id) \
		       + self.anonymous_views

	def views_by_user(self, user):
		return LessonResourceUserAccess.count_access(self.id, user.id)

	def log_user_view(self, user):
		LessonResourceUserAccess.log_user_access(self.id, user.id)

	def log_anonymous_view(self):
		self.anonymous_views += 1

	@property
	def icon(self):
		stubs = {
			'google_doc': 'fa-file-alt',
			'google_sheet': 'fa-file-spreadsheet',
			'google_slides': 'fa-file-image'
		}
		if self.type in stubs:
			return stubs[self.type]
		return 'fa-file'

	@property
	def description(self):
		stubs = {
			'google_doc': 'Google document',
			'google_sheet': 'Google spreadsheet',
			'google_slides': 'Google slides'
		}
		if self.type in stubs:
			return stubs[self.type]
		return 'External file'

	@property
	def permalink(self):
		return url_for('resource.view', resource_id=self.id)

	@staticmethod
	def find_by_id(resource_id):
		session = get_session()
		return session.query(Resource).filter(Resource.id == resource_id).first()


class LessonResourceUserAccess(Base):
	__tablename__ = "resource_user_access"
	id = sa.Column(sa.Integer, primary_key=True)
	resource_id = sa.Column(sa.Integer, sa.ForeignKey('lesson_resources.id'))
	user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
	access_date = sa.Column(sa.DateTime, default=datetime.utcnow)

	@staticmethod
	def count_access(resource_id, user_id=None):
		session = get_session()
		q = session.query(sa.func.count(LessonResourceUserAccess.id)).\
			filter(LessonResourceUserAccess.resource_id == resource_id)
		if user_id is not None:
			q = q.filter(LessonResourceUserAccess.user_id == user_id)
		return q.all()[0][0]

	@staticmethod
	def log_user_access(resource_id, user_id):
		session = get_session()
		log = LessonResourceUserAccess(resource_id=resource_id, user_id=user_id)
		q = session.query(LessonResourceUserAccess).\
			filter(LessonResourceUserAccess.resource_id == resource_id)
		session.add(log)
		session.commit()


class SegmentUserProgress(Base):
	__tablename__ = "segment_user_progress"
	id = sa.Column(sa.Integer, primary_key=True)
	progress = sa.Column(sa.Integer)
	# No complex join definition for now.
	segment_id = sa.Column(sa.Integer, sa.ForeignKey('lesson_segments.id'))
	user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))


_session = None
def get_session():
	global _session
	if _session is None:
		engine = sa.create_engine(app.config['DB_URI'])
		Base.metadata.create_all(engine)
		Session = orm.scoped_session(orm.sessionmaker(bind=engine))
		_session = Session()
	return _session

def _clear_session_for_tests():
	global _session
	if 'FLASK_ENV' not in environ or environ['FLASK_ENV'] != 'test':
		raise Exception("Session clearing is for test instances only.")
	_session = None


def get_user(user_id):
	return User.find_by_id(user_id)

def get_user_by_email(email):
	return User.find_by_email(email)

def get_course_by_slug(slug):
	return Course.find_by_slug(slug)

def get_course_by_code(code):
	return Course.find_by_code(code)

def get_public_courses():
	session = get_session()
	return session.query(Course).filter(Course.guest_access == True).all()

def get_program_by_slug(slug):
	return Program.find_by_slug(slug)

def get_lesson(lesson_id):
	return Lesson.find_by_id(lesson_id)

def get_lesson_by_slug(course_slug, lesson_slug):
	return Lesson.find_by_slug(course_slug, lesson_slug)

def get_segment(segment_id):
	return Segment.find_by_id(segment_id)

def get_segment_by_slug(course_slug, lesson_slug, segment_slug):
	return Segment.find_by_slug(course_slug, lesson_slug, segment_slug)

def get_segment_progress(segment_id, user_id):
	return Segment.find_user_progress(segment_id, user_id)

def save_segment_progress(segment_id, user_id, percent):
	session = get_session()
	sup = get_segment_progress(segment_id, user_id)
	percent = int(percent)
	if sup is None:
		sup = SegmentUserProgress(segment_id=segment_id, user_id=user_id, progress=percent)
	elif sup.progress < percent:
		sup.progress = percent
	session.add(sup)
	session.commit()
	return sup

def get_enrollment(course_id, student_id):
	return CourseEnrollment.find_by_course_and_student(course_id, student_id)

def fetch_thumbnail(wistia_id, width=640, height=360):
	""" TODO: Put this in an S3 bucket before returning the URL. """
	url = 'http://fast.wistia.net/oembed?url=http://home.wistia.com/medias/{}?embedType=async&videoWidth=640'.\
	      format(wistia_id)
	data = requests.get(url).json()
	return data['thumbnail_url'].split('?')[0]+'?image_crop_resized={}x{}'.format(width, height)