from flask import (redirect, url_for, make_response)
from flask.views import MethodView

from app.shared.constants import COOKIE_KEY


class LogoutView(MethodView):
    def get(self):
        response = make_response(redirect(url_for('auth.login')))
        response.delete_cookie('auth_discharge')
        return response
