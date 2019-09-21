from wtforms import (
    Form,
    BooleanField,
    StringField,
    validators,
    TextAreaField,
    FileField,
)


class AddLessonForm(Form):
    title = StringField("Title", [validators.Length(min=4, max=50)])
    description = StringField("Description", [validators.Length(min=6, max=140)])
    cover_image = FileField("Cover image")
