from flask import render_template


def render_question_answer(course, lesson, question):
    data = {"course": course, "lesson": lesson, "question": question}
    return render_template("partials/course/_qa.html", **data)


def render_teacher(teacher, course, lesson=None):
    data = {"teacher": teacher, "course": course, "lesson": lesson}

    return render_template("partials/course/_teacher.html", **data)


def render_intro(introduction):
    data = {"introduction": introduction}

    return render_template("partials/course/_intro.html", **data)


def render_segment_list_element(course, lesson, segment):
    data = {"segment": segment,
            "course": course,
            "lesson": lesson}

    return render_template("partials/course/_list_segment_element.html", **data)
