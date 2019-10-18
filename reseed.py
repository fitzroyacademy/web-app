import datamodels
import copy

session = datamodels.get_session()

import stubs

def get_seconds(dur):
	mmss = dur.split(":")  # no edge cases, we're handling stub data
	return int(mmss[0]) * 60 + int(mmss[1])

for student in stubs.students:
	user = copy.deepcopy(student)
	password = user.pop('password')
	u = datamodels.User(**user)
	u.password = password
	session.add(u)

session.commit()

c = datamodels.Course(
	title="Into to Social Enterprise",
	slug="fitzroy-academy",
	course_code="abc123",
	target_audience="Super early stage social enterprise founders, starting your first business or a new project from scratch.",
	skill_level="Introduction.",
	visibility="public",
	info="Start here! Basic business models and customer discovery, to pitching for investment. ❤️ 🚀",
	workload_summary="This course will take 20-30 hours on average, and is best done in teams.",
	summary_html="""
<p><strong>Go from zero to one:</strong> From a basic idea to early customers, business models and getting the numbers right.</p>
<p>We don't need any previous business experience, but by the end you'll cover quite complex topics like financial modelling, </p>
<p><strong>On the social impact</strong> side of things, you'll define your impact model, look into creating behaviour change that lasts, and maybe even think about partnering with another organisation to create impact.</p>
""",
	preview_thumbnail="/assets/images/lessons/customer-interviews.jpg",
	guest_access=True,
	draft=False
)
c.add_instructor(datamodels.get_user(1))  # Homer
c.add_instructor(datamodels.get_user(2))  # Marge
session.add(c)

for i, lesson in enumerate(stubs.lessons):
	lesson = copy.deepcopy(lesson)
	resources = lesson.pop('resources')
	segments = lesson.pop('segments')
	lesson.pop('id')
	lesson.pop('course_id')
	lesson["order"] = i
	lesson["language"] = "en"
	l = datamodels.Lesson(**lesson)
	l.course = c
	c.lessons.append(l)
	session.add(l)
	session.commit()
	for j, segment in enumerate(segments):
		segment = copy.deepcopy(segment)
		segment['duration_seconds'] = get_seconds(segment.pop('duration'))
		segment.pop('lesson_id')
		segment.pop('course_id')
		segment.pop('template')  # ultimately derived from external URL
		segment['slug'] = segment.pop('id')
		segment["order"] = j
		segment["language"] = "en"
		s = datamodels.Segment(**segment)
		l.segments.append(s)
		s.lesson = l
		session.add(s)
	for j, resource in enumerate(resources):
		resource = copy.deepcopy(resource)
		resource['language'] = resource.pop('lang')
		resource['slug'] = resource.pop('id')
		resource['order'] = j
		r = datamodels.Resource(**resource)
		r.lesson = l
		l.resources.append(r)
		session.add(r)
	session.commit()
