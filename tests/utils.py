import datetime

from slugify import slugify

import datamodels
from enums import SegmentPermissionEnum
from app import app


def make_authorized_call(
    url, user, data=None, expected_status_code=200, follow_redirects=False
):
    s = app.test_client()
    with s.session_transaction() as sess:
        sess["user_id"] = user.id
    response = s.post(url, data=data, follow_redirects=follow_redirects)
    assert response.status_code == expected_status_code

    return response


def make_call(url, user, expected_status_code=200, follow_redirects=False):
    s = app.test_client()
    with s.session_transaction() as sess:
        sess["user_id"] = user.id
    response = s.get(url, follow_redirects=follow_redirects)
    print(response.status_code, expected_status_code)
    assert response.status_code == expected_status_code

    return response


class ObjectsGenerator(object):
    @staticmethod
    def make_standard_course(
        code="ABC123", guest_access=False, title="ABC 123", slug=None, draft=False
    ):
        if slug is None:
            slug = slugify(title)
        course = datamodels.Course(
            course_code=code,
            title=title,
            slug=slug,
            guest_access=guest_access,
            draft=draft,
        )
        return course

    @staticmethod
    def make_standard_course_lesson(
        course, title="Lesson", active=True, language="EN", slug=None, order=1
    ):
        if slug is None:
            slug = slugify(title)
        lesson = datamodels.Lesson(
            course=course,
            title=title,
            active=active,
            language=language,
            slug=slug,
            order=order,
        )
        return lesson

    @staticmethod
    def make_segment(
        lesson,
        thumbnail="thumbnail_1",
        title="Segment",
        duration_seconds=200,
        url="fitzroyacademy.com",
        order=1,
        slug=None,
        type="text",
        permission=None,
    ):
        if slug is None:
            slug = slugify(title)
        if permission is None:
            permission = SegmentPermissionEnum.normal
        segment = datamodels.Segment(
            title=title,
            duration_seconds=duration_seconds,
            url=url,
            language="EN",
            order=order,
            _thumbnail=thumbnail,
            lesson=lesson,
            slug=slug,
            type=type,
            permission=permission,
        )
        return segment

    @staticmethod
    def makeUser(
        id=1,
        first_name="Homer",
        last_name="Simpson",
        email="homer@simpsons.com",
        username="homer",
        password="password",
        phone_number="555-444-1234",
        dob=None,
    ):
        dob = dob or datetime.datetime.now()
        u = datamodels.User(
            id=id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            phone_number=phone_number,
            dob=dob,
        )
        u.password = password
        return u
