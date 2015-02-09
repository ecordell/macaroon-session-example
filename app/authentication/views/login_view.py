from flask import (request, render_template,
                   flash, redirect, url_for, make_response, g, current_app)
from flask.views import MethodView

from app.shared.functions import (set_session_cookie, get_session_and_discharge)
from app.authentication.forms import LoginForm
from app.tokens.user_session import UserSessionFactory, UserSessionValidator


class LoginView(MethodView):

    def __init__(self):
        super().__init__()
        self.redis = g.redis
        self.logger = current_app.logger

    def get(self):
        form = LoginForm(request.form)
        try:
            session, discharge = get_session_and_discharge(request)
            valid_session = UserSessionValidator().verify(session, discharge)
            if valid_session:
                return render_template(
                    "auth/logged_in.html"
                )
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

                session_macaroon, session_signature, auth_discharge = (
                    UserSessionFactory(
                        username=form.email.data
                    ).create_tokens()
                )
                response = make_response(render_template(
                    "auth/logged_in.html",
                    form=form
                ))
                set_session_cookie(
                    response,
                    session_macaroon,
                    session_signature,
                    auth_discharge
                )
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
