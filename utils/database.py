import copy
import json

import sqlalchemy as sa

import datamodels
from utils import stubs


def get_seconds(dur):
    mmss = dur.split(":")  # no edge cases, we're handling stub data
    return int(mmss[0]) * 60 + int(mmss[1])


def dump(obj, seen=None):
    if not isinstance(obj, datamodels.base.Base):
        if isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], datamodels.base.Base):
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
    for f in [x for x in dir(obj) if x.startswith("_") is False and x not in ignored]:
        data = getattr(obj, f)
        try:

            json.dumps(data)
            fields[f] = data
        except TypeError:
            if isinstance(data, sa.orm.query.Query):
                fields[f[4:]] = None
            elif isinstance(data, datamodels.base.Base):
                if id(data) in seen:
                    fields[f] = None
                else:
                    fields[f] = dump(data, seen)
            elif callable(data) and f.startswith("get_"):
                _data = data()
                if isinstance(_data, sa.orm.query.Query):
                    fields[f[4:]] = None
                else:
                    fields[f[4:]] = dump(_data, seen)
            elif isinstance(data, list):
                fields[f] = []
                for o in data:
                    if id(o) in seen:
                        fields[f].append(None)
                    else:
                        fields[f].append(dump(o, seen))
    return fields



def reseed():
    session = datamodels.get_session()

    for student in stubs.students:
        user = copy.deepcopy(student)
        password = user.pop("password")
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
        preview_thumbnail="/static/assets/images/lessons/customer-interviews.jpg",
        guest_access=True,
        draft=False,
        workload_title="",
        workload_subtitle="",
    )
    c.add_instructor(datamodels.get_user(1))  # Homer
    c.add_instructor(datamodels.get_user(2))  # Marge
    session.add(c)

    for i, lesson in enumerate(stubs.lessons):
        lesson = copy.deepcopy(lesson)
        resources = lesson.pop("resources")
        segments = lesson.pop("segments")
        lesson.pop("id")
        lesson.pop("course_id")
        lesson["order"] = i
        lesson["language"] = "en"
        l = datamodels.Lesson(**lesson)
        l.course = c
        c.lessons.append(l)
        session.add(l)
        session.commit()
        for j, segment in enumerate(segments):
            segment = copy.deepcopy(segment)
            segment["duration_seconds"] = get_seconds(segment.pop("duration"))
            segment.pop("lesson_id")
            segment.pop("course_id")
            segment.pop("template")  # ultimately derived from external URL
            segment["slug"] = segment.pop("id")
            segment["order"] = j
            segment["language"] = "en"
            s = datamodels.Segment(**segment)
            l.segments.append(s)
            s.lesson = l
            session.add(s)
        for j, resource in enumerate(resources):
            resource = copy.deepcopy(resource)
            resource["language"] = resource.pop("lang")
            resource["slug"] = resource.pop("id")
            resource["order"] = j
            r = datamodels.Resource(**resource)
            r.lesson = l
            l.resources.append(r)
            session.add(r)
        session.commit()

    # default institute, whitout subdomain
    fitz_institute = datamodels.Institute(name="Fitzroyacademy", logo="", slug="")

    session.add(fitz_institute)
    session.commit()

    fitz_institute.add_admin(datamodels.get_user(1))  # Homer

    institute1 = datamodels.Institute(name="Jedi Temple", logo="", slug="jeditemple")

    session.add(institute1)
    session.commit()

    institute1.add_admin(datamodels.get_user(3))  # Bart
    session.commit()
