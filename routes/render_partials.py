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

    data = {"user": user,
            "obj": obj,
            "lesson": lesson,
            "data_type": data_type,
            "user_type": user_type
            }

    return render_template("partials/course/_teacher.html", **data)
