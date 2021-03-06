from flask import redirect, abort, flash, request, jsonify
from slugify import slugify

import datamodels
from dataforms import AddResourceForm
from datamodels.enums import ResourceTypeEnum
from utils.base import get_current_user
from .decorators import login_required, teacher_required
from .utils import reorder_items, clone_model
from .blueprint import SubdomainBlueprint
from .render_partials import render_resource_list_element

blueprint = SubdomainBlueprint("resource", __name__, template_folder="templates")


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/<int:resource_id>/delete",
    methods=["POST"],
)
@login_required
@teacher_required
def delete_resource(user, course, course_slug, lesson_id, resource_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    resource = datamodels.Resource.find_by_id(resource_id)
    if lesson and resource and lesson.id == resource.lesson_id:
        resource.delete(resource, parent=lesson, key="lesson_id")

        return jsonify(
            {"success_url": "/course/{}/lessons/{}/edit".format(course_slug, lesson_id)}
        )

    return jsonify({"success": False, "message": "Couldn't delete resource"}), 400


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/reorder", methods=["POST"]
)
@login_required
@teacher_required
def reorder_resources(user, course, course_slug, lesson_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        return "Lesson not found", 400
    return reorder_items(request, datamodels.Resource, lesson.resources)


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/<int:resource_id>/edit",
    methods=["POST"],
)
@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/add", methods=["POST"]
)
@login_required
@teacher_required
def add_resource(user, course, course_slug, lesson_id, resource_id=None, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        return abort(404)

    if resource_id:
        instance = datamodels.Resource.find_by_id(resource_id)
        if not lesson or instance and instance.lesson_id != lesson.id:
            return abort(404)
    else:
        instance = datamodels.Resource(lesson=lesson, order=len(lesson.resources) + 1)

    errors = []
    form = AddResourceForm(request.form)
    if form.validate():
        instance.url = form.resource_url.data
        instance.title = form.resource_title.data
        instance.type = getattr(ResourceTypeEnum, form.resource_type.data)
        instance.slug = slugify(form.resource_title.data)
        instance.description = form.resource_description.data
        instance.featured = form.resource_featured.data

        db = datamodels.get_session()
        db.add(instance)
        db.commit()

        return jsonify(
            {
                "html": render_resource_list_element(
                    course=course, lesson=lesson, resource=instance
                ),
                "message": "Resource updated" if resource_id else "Resource created",
                "id": instance.id,
            }
        )
    else:
        errors = [error for error in form.errors.values()]

    return (
        jsonify(
            {"message": "There were errors when saving resource data", "errors": errors}
        ),
        400,
    )


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/<int:resource_id>/edit",
    methods=["GET"],
)
@login_required
@teacher_required
def edit_resource(user, course, course_slug, lesson_id, resource_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    resource = datamodels.Resource.find_by_id(resource_id)

    if not lesson or resource and resource.lesson_id != lesson.id:
        return jsonify({"message": "Wrong lesson or resource"}), 400
    else:
        return jsonify(
            {
                "url": resource.url,
                "title": resource.title,
                "type": resource.type.name,
                "description": resource.description,
                "featured": resource.featured,
            }
        )


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/<int:resource_id>/copy",
    methods=["GET"],
)
@login_required
@teacher_required
def copy_resource(user, course, course_slug, lesson_id, resource_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    resource = datamodels.Resource.find_by_id(resource_id)

    if not lesson or resource and resource.lesson_id != lesson.id:
        flash("Lesson or resource do not match course or lesson")
        return redirect("/course/{}/edit".format(course.slug))

    resource_copy = clone_model(resource)
    resource_copy.title = resource.title + "_copy"
    resource_copy.slug = slugify(resource_copy.title)
    resource_copy.order = len(lesson.resources) + 1

    if resource_copy.slug:
        db = datamodels.get_session()
        db.add(resource_copy)
        db.commit()

        flash("Resource duplicated")

    return redirect("/course/{}/lessons/{}/edit".format(course.slug, lesson_id))


@blueprint.subdomain_route("/resources/<resource_id>")
def view(resource_id, institute=""):
    """
    Proxy for resource links which logs access then redirects the user.
    """
    resource = datamodels.Resource.find_by_id(resource_id)
    if resource is None:
        abort(404)
    user = get_current_user()
    if user is not None:
        resource.log_user_view(user)
    else:
        resource.log_anonymous_view()
    return redirect(resource.url)
