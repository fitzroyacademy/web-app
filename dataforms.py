from wtforms import Form, StringField, validators, TextAreaField, FileField

from enums import ResourceTypeEnum
from werkzeug.utils import cached_property

from flask import session, current_app
from wtforms.csrf.session import SessionCSRF


class CSRFBaseForm(Form):
    class Meta:
        csrf_class = SessionCSRF

        @cached_property
        def csrf_secret(self):
            return current_app.config.get('WTF_CSRF_SECRET', True)

        @property
        def csrf_context(self):
            return session

        @cached_property
        def csrf(self):
            return current_app.config.get('WTF_CSRF_ENABLED', True)


class AjaxCSRFTokenForm(CSRFBaseForm):
    pass


class EditUserForm(CSRFBaseForm):
    email = StringField("email", [validators.required(), validators.Email()])
    first_name = StringField("First name", [validators.required()])
    last_name = StringField("Last name", [validators.required()])
    username = StringField("Username", [validators.required(), validators.Length(max=50)])
    password = StringField("Password")


class AddUserForm(EditUserForm):
    password = StringField("Password", [validators.required()])


class LoginForm(CSRFBaseForm):
    email = StringField("email", [validators.required()])
    password = StringField("password", [validators.required()])


class AddLessonForm(CSRFBaseForm):
    title = StringField("Title", [validators.Length(min=4, max=50)])
    description = StringField("Description", [validators.Length(min=6, max=140)])
    further_reading = StringField("Further reading")
    cover_image = FileField("Cover image")


class AddResourceForm(CSRFBaseForm):
    resource_title = StringField("Title", [validators.required()])
    resource_url = StringField("Link", [validators.required(), validators.URL()])
    resource_description = TextAreaField("Description")
    resource_type = StringField(
        "Content type",
        [validators.required(), validators.AnyOf([e.name for e in ResourceTypeEnum])],
    )


class AddCourseForm(CSRFBaseForm):
    title = StringField("Title", [validators.required(), validators.Length(min=4, max=50)])
    info = StringField("Description", [validators.required(), validators.Length(min=4, max=140)])


class LessonQAForm(CSRFBaseForm):
    question = StringField(
        "Question", [validators.required(), validators.Length(min=3)]
    )
    answer = StringField("Answer", [validators.required(), validators.Length(min=3)])


class ReorderForm(CSRFBaseForm):
    items_order = StringField("Ordered items", [validators.required()])
