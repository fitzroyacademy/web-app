from flask import render_template


def render_question_answer(course, lesson, question):
    data = {"course": course, "lesson": lesson, "question": question}
    return render_template("partials/course/_qa.html", **data)


def render_teacher(user, course=None, lesson=None, institute=None, user_type="teacher"):
    if institute:
        lesson = None
        data_type = "institute"
    else:
        data_type = "course"

    obj = course or institute

    data = {
        "user": user,
        "obj": obj,
        "lesson": lesson,
        "data_type": data_type,
        "user_type": user_type,
    }

    return render_template("partials/course/_teacher.html", **data)


def render_intro(introduction):
    data = {"introduction": introduction}

    return render_template("partials/course/_intro.html", **data)


def render_segment_list_element(course, lesson, segment):
    data = {"segment": segment, "course": course, "lesson": lesson}

    return render_template("partials/course/_list_segment_element.html", **data)


def render_resource_list_element(course, lesson, resource):
    data = {"resource": resource, "course": course, "lesson": lesson}

    return render_template("partials/course/_list_resource_element.html", **data)


def render_segment_modal(segment_type, course, lesson, surveys):

    data = {"course": course, "lesson": lesson}

    if segment_type == "survey":

        type_choices_html = render_template(
            "partials/surveys/_type_choices.html", surveys_type_choices=surveys
        )

        rendered_survey_types = [
            render_template(
                "partials/surveys/_type_{}.html".format(survey["survey_type"]),
                survey=survey,
            )
            for survey in surveys
        ]

        data["type_choices_html"] = type_choices_html
        data["rendered_survey_types"] = rendered_survey_types
    return render_template(
        "partials/modal/_add_{}_segment.html".format(segment_type), **data
    )
