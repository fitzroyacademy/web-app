import copy

import datamodels
from datamodels.enums import SegmentType
from utils import stubs


def get_seconds(dur):
    mmss = dur.split(":")  # no edge cases, we're handling stub data
    return int(mmss[0]) * 60 + int(mmss[1])


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
        <p><strong>On the social impact</strong> side of things, you'll define your impact model, look into creating behaviour
        change that lasts, and maybe even think about partnering with another organisation to create impact.</p>
        """,
        cover_image="/static/assets/images/lessons/customer-interviews.jpg",
        guest_access=True,
        draft=False,
        workload_title="",
        workload_subtitle="",
    )
    session.add(c)
    session.commit()

    c.add_instructor(datamodels.get_user(1))  # Homer
    c.add_instructor(datamodels.get_user(2))  # Marge

    c.enroll(datamodels.get_user(3))  # Bart
    c.enroll(datamodels.get_user(4))  # Lisa
    c.enroll(datamodels.get_user(5))  # Maggie
    session.add(c)
    session.commit()

    for i, lesson in enumerate(stubs.lessons):
        lesson = copy.deepcopy(lesson)
        resources = lesson.pop("resources")
        segments = lesson.pop("segments")
        lesson.pop("id")
        lesson.pop("course_id")
        lesson["language"] = "en"
        new_lesson = datamodels.Lesson(**lesson)
        new_lesson.course = c
        c.lessons.append(new_lesson)
        session.add(new_lesson)
        session.commit()
        for j, segment in enumerate(segments):
            segment = copy.deepcopy(segment)
            segment["duration_seconds"] = get_seconds(segment.pop("duration"))
            segment.pop("lesson_id")
            segment.pop("course_id")
            segment.pop("template")  # ultimately derived from external URL
            segment["slug"] = segment.pop("id")
            segment["language"] = "en"
            segment["type"] = SegmentType.video
            s = datamodels.Segment(**segment)
            new_lesson.segments.append(s)
            s.lesson = new_lesson
            session.add(s)
        for j, resource in enumerate(resources):
            resource = copy.deepcopy(resource)
            resource["language"] = resource.pop("lang")
            resource["slug"] = resource.pop("id")
            resource["order"] = j
            r = datamodels.Resource(**resource)
            r.lesson = new_lesson
            new_lesson.resources.append(r)
            session.add(r)
        session.commit()

    for user_progress in stubs.user_segment_progress:
        user = datamodels.User.find_by_email(user_progress["email"])
        for lesson in user_progress["lessons"]:
            for slug, progress in lesson["progress"].items():
                # we can search segments by slug because in stubs segments slugs are unique
                segment = (
                    datamodels.Segment.objects()
                    .filter(datamodels.Segment.slug == slug)
                    .first()
                )
                datamodels.SegmentUserProgress.save_user_progress(
                    segment.id, user.id, progress
                )

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
