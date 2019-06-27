import datamodels
import copy

session = datamodels.get_session()

import stubs

def get_seconds(dur):
	mmss = dur.split(":")  # no edge cases, we're handling stub data
	return int(mmss[0]) * 60 + int(mmss[1])

for student in stubs.students:
	u = datamodels.User(**student)
	session.add(u)

c = datamodels.Course(slug="fitzroy-academy")
session.add(c)

for i, lesson in enumerate(stubs.lessons):
	lesson = copy.deepcopy(lesson)
	resources = lesson.pop('resources')
	segments = lesson.pop('segments')
	lesson.pop('id')
	lesson.pop('course_id')
	lesson['duration_seconds'] = get_seconds(lesson.pop('duration'))
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
