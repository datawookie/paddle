from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from ..views.common import db, session

PASSWORD_LENGTH_MIN = 8
PASSWORD_LENGTH_MAX = 72
#
PASSWORD_LENGTH_VALIDATOR = Length(min=PASSWORD_LENGTH_MIN, max=PASSWORD_LENGTH_MAX)


class LoginForm(FlaskForm):
    email = EmailField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), PASSWORD_LENGTH_VALIDATOR])
    submit = SubmitField("Submit")


class RegisterForm(LoginForm):
    cpwd = PasswordField(
        validators=[
            InputRequired(),
            PASSWORD_LENGTH_VALIDATOR,
            EqualTo("pwd", message="Passwords must match!"),
        ]
    )

    def validate_email(self, email):
        if session.query(db.User).filter_by(email=email.data).first():
            raise RuntimeError("Email already registered!")
