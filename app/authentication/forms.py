from flask_wtf import Form

from wtforms.fields import TextField, PasswordField, BooleanField
from wtforms.validators import Required, Email


class LoginForm(Form):
    email = TextField(
        'Email Address',
        [
            Email(),
            Required(message='Forgot your email address?')
        ]
    )
    password = PasswordField(
        'Password',
        [
            Required(message='Must provide a password.')
        ]
    )
    remember = BooleanField(
        'Remember Me'
    )


class SignupForm(Form):
    email = TextField(
        'Email Address',
        [
            Email(),
            Required(message='Must provide an email address.')
        ]
    )
    password = PasswordField(
        'Password',
        [
            Required(message='Must provide a password.')
        ]
    )
