from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm as orm
import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):

	__tablename__ = 'users'

	id = sa.Column(sa.Integer, primary_key=True)
	full_name = sa.Column(sa.String)
	email = sa.Column(sa.String, unique=True)
	password_hash = sa.Column(sa.String(128))

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


class Institute(Base):

	__tablename__ = 'institutes'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String)
	logo = sa.Column(sa.String)  # URL to picture resource

	# colour_choice (???) themes of some sort

	# We probably want admin to be many-to-many
	# admin_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
	# admin = orm.relationship("User")


class Program(Base):

	__tablename__ = 'programs'

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String)

	# We probably want admin to be many-to-many
	# admin_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
	# admin = orm.relationship("User")


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

	def __repr__(self):
		return ":D"


class Lesson(Base):

	__tablename__ = 'lessons'

	id = sa.Column(sa.Integer, primary_key=True)
	title = sa.Column(sa.String)
	duration_seconds = sa.Column(sa.Integer) # derivable through children
	active = sa.Column(sa.Boolean)

	course_id = sa.Column(sa.Integer, sa.ForeignKey('courses.id'))
	course = orm.relationship("Course", back_populates="lessons")

	def __repr__(self):
		return ":D"


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

	def __repr__(self):
		return ":D"


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

	def __repr__(self):
		return ":D"

db_endpoint = os_environ['DB_ENDPOINT']
engine = sa.create_engine(db_endpoint)
Base.metadata.create_all(engine)