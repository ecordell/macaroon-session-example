from flask import (request, render_template,
                   make_response, g, current_app)
from flask.views import MethodView

from app.utils import get_session_and_discharge, expire_time_from_duration
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
                self._set_session_cookie(
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

    def _set_session_cookie(
        self, response, session_macaroon, session_signature, auth_discharge
    ):
        response.set_cookie(
            current_app.config['SESSION_COOKIE_KEY'],
            value=session_macaroon,
            max_age=None,
            expires=None,
            path='/',
            domain=None,
            secure=False,
            httponly=True
        )
        response.set_cookie(
            current_app.config['SESSION_SIGNATURE_KEY'],
            value=session_signature,
            max_age=None,
            expires=None,
            path='/',
            domain=None,
            secure=False,
            httponly=False
        )
        response.set_cookie(
            current_app.config['AUTH_REFRESH_DISCHARGE_KEY'],
            value=auth_discharge,
            max_age=None,
            expires=expire_time_from_duration(
                current_app.config['SESSION_LENGTH']
            ).timestamp,
            path='/',
            domain=None,
            secure=False,
            httponly=False
        )
        response.set_cookie(
            current_app.config['MAX_SESSION_REFRESH_KEY'],
            value=str(expire_time_from_duration(
                current_app.config['MAX_SESSION_REFRESH_LENGTH']
            )),
            max_age=None,
            expires=expire_time_from_duration(
                current_app.config['MAX_SESSION_REFRESH_LENGTH']
            ).timestamp,
            path='/',
            domain=None,
            secure=False,
            httponly=False
        )
