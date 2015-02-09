from flask import (request, render_template,
                   g, current_app)
from flask.views import MethodView
from pymacaroons import Macaroon

from app.utils import get_session_and_discharge
from app.tokens.user_session import UserSessionValidator


class RefreshAuthView(MethodView):

    def __init__(self):
        super().__init__()
        self.redis = g.redis
        self.logger = current_app.logger
        self.context = {}

    def get(self):
        try:
            session, discharge = get_session_and_discharge(request)
            valid_session = UserSessionValidator().verify(session, discharge)
            if valid_session:
                self.context['discharge_secret'] = (
                    self._get_secret_for_discharge(discharge)
                )
            else:
                self.context['discharge_secret'] = ''
        except Exception as e:
            self.logger.exception(e)
        return render_template("auth/refresh_auth.html", **self.context)

    def _get_secret_for_discharge(self, discharge):
        discharge_macaroon = Macaroon.from_binary(discharge)
        return self.redis.get(discharge_macaroon.identifier).decode('ascii')
