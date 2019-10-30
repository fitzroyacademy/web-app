import datetime

from slugify import slugify

import datamodels
from enums import SegmentPermissionEnum, ResourceTypeEnum
from app import app


def make_authorized_call(
    url, user, data=None, expected_status_code=200, follow_redirects=False, method="post"
):
    s = app.test_client()
    with s.session_transaction() as sess:
        sess["user_id"] = user.id
    if method == "post":
        response = s.post(url, data=data, follow_redirects=follow_redirects)
    else:
        response = s.get(url, follow_redirects=follow_redirects)
    assert response.status_code == expected_status_code

    return response


class ObjectsGenerator(object):
    @staticmethod
    def make_standard_course(
        code="ABC123", guest_access=False, title="ABC 123", slug=None, draft=False, visibility="public", paid=False
    ):
        if slug is None:
            slug = slugify(title)
        course = datamodels.Course(
            course_code=code,
            title=title,
            slug=slug,
            guest_access=guest_access,
            draft=draft,
            paid=paid,
            visibility=visibility
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
    def make_resource(
            lesson,
            title="Resource 1",
            url="https://fitzroyacademy.com/blah-blah-blah",
            featured=False,
            language="EN",
            description="Some long text describing this resource which is optional",
            order=1,
            slug=None,
            resource_type=None,
    ):
        if resource_type is None:
            resource_type = ResourceTypeEnum.google_doc
        if slug is None:
            slug = slugify(title)
        resource = datamodels.Resource(
            title=title,
            url=url,
            featured=featured,
            language=language,
            description=description,
            order=order,
            lesson=lesson,
            slug=slug,
            type=resource_type
        )
        return resource

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
