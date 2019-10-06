from wtforms import Form, StringField, validators, TextAreaField, FileField

from enums import ResourceTypeEnum


class AddLessonForm(Form):
    title = StringField("Title", [validators.Length(min=4, max=50)])
    description = StringField("Description", [validators.Length(min=6, max=140)])
    cover_image = FileField("Cover image")


class AddResourceForm(Form):
    resource_title = StringField("Title", [validators.required()])
    resource_url = StringField("Link", [validators.required(), validators.URL()])
    resource_description = TextAreaField("Description")
    resource_type = StringField(
        "Content type",
        [validators.required(), validators.AnyOf([e.name for e in ResourceTypeEnum])],
    )


class LessonQAForm(Form):
    question = StringField(
        "Question", [validators.required(), validators.Length(min=3)]
    )
    answer = StringField("Answer", [validators.required(), validators.Length(min=3)])
