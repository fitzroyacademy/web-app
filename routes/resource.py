from flask import Blueprint, redirect, abort, flash, request, jsonify, render_template
from slugify import slugify

import datamodels
from dataforms import AddResourceForm
from enums import ResourceTypeEnum
from utils.base import get_current_user
from .decorators import login_required, teacher_required
from .utils import reorder_items, clone_model

blueprint = Blueprint("resource", __name__, template_folder="templates")


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/<int:resource_id>/delete",
    methods=["POST"],
)
@login_required
@teacher_required
def delete_resource(user, course, course_slug, lesson_id, resource_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
    resource = datamodels.Resource.find_by_id(resource_id)
    if lesson and resource and lesson.id == resource.lesson_id:
        resource.delete(resource, parent=lesson, key="lesson_id")

        return jsonify(
            {"success_url": "/course/{}/lessons/{}/edit".format(course_slug, lesson_id)}
        )

    return jsonify({"success": False, "message": "Couldn't delete resource"}), 400


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/reorder", methods=["POST"]
)
@login_required
@teacher_required
def reorder_resources(user, course, course_slug, lesson_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        return "Lesson not found", 400
    return reorder_items(request, datamodels.Resource, lesson.resources)


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/<int:resource_id>/edit",
    methods=["POST"],
)
@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/add", methods=["POST"]
)
@login_required
@teacher_required
def add_resource(user, course, course_slug, lesson_id, resource_id=None):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        return abort(404)

    if resource_id:
        instance = datamodels.Resource.find_by_id(resource_id)
        if not lesson or instance and instance.lesson_id != lesson.id:
            return abort(404)
    else:
        instance = datamodels.Resource(lesson=lesson, order=len(lesson.resources) + 1)

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
        if resource_id:
            flash("Resource updated")
        else:
            flash("Resource created")
    else:
        for error in form.errors.values():
            flash(error)

    return redirect("/course/{}/lessons/{}/edit".format(course.slug, lesson.id))


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/<int:resource_id>/edit",
    methods=["GET"],
)
@login_required
@teacher_required
def edit_resource(user, course, course_slug, lesson_id, resource_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
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
                "featured": resource.featured
            }
        )


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/resources/<int:resource_id>/copy",
    methods=["GET"],
)
@login_required
@teacher_required
def copy_resource(user, course, course_slug, lesson_id, resource_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
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


@blueprint.route("<resource_id>")
def view(resource_id):
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
