from flask import (request, render_template,
                   flash, redirect, url_for, make_response)
from flask.views import MethodView

from app.service_locator import ServiceLocator
from app.shared.constants import COOKIE_KEY
from app.shared.functions import set_session_cookie
from app.authentication.forms import LoginForm
from app.tokens.user_session import UserSessionFactory, UserSessionValidator


class LoginView(MethodView):

    def __init__(self):
        super().__init__()
        self.redis = ServiceLocator.get_redis()
        self.logger = ServiceLocator.get_logger()

    def get(self):
        form = LoginForm(request.form)
        try:
            if COOKIE_KEY in request.cookies:
                session = request.cookies.get(COOKIE_KEY)
                valid_session = UserSessionValidator().verify(session)
                if valid_session:
                    return render_template(
                        "auth/logged_in.html"
                    )
                else:
                    return redirect(url_for('auth.logout'))
        except Exception as e:
            self.logger.exception(e)
        return render_template("auth/login.html", form=form)

    def post(self):
        form = LoginForm(request.form)

        if form.validate_on_submit():
            try:
                self._authenticate_credentials(
                    form.email.data,
                    form.password.data
                )

                flash('Welcome')

                session_token = UserSessionFactory(
                    username=form.email.data
                ).create_token()

                response = make_response(render_template(
                    "auth/login.html",
                    form=form
                ))
                set_session_cookie(response, session_token)
                return response
            except Exception as e:
                self.logger.exception(e)

        return render_template("auth/login.html", form=form)

    def _authenticate_credentials(self, username, password):
        stored_password = self.redis.get(username).decode('utf-8')
        if stored_password != password:
            raise Exception(
                'Invalid Credentials: got {given}, expected {expected}'.format(
                    given=password, expected=stored_password
                )
            )
