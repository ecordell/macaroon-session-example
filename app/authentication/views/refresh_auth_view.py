from flask import (request, render_template,
                   flash, redirect, url_for, make_response)
from flask.views import MethodView
from pymacaroons import Macaroon

from app.service_locator import ServiceLocator
from app.shared.functions import get_session_and_discharge, get_config
from app.tokens.user_session import UserSessionValidator


class RefreshAuthView(MethodView):

    def __init__(self):
        super().__init__()
        self.redis = ServiceLocator.get_redis()
        self.logger = ServiceLocator.get_logger()

    def get(self):
        context = {
            'origin': get_config('SERVER_NAME')
        }
        try:
            session, discharge = get_session_and_discharge(request)
            valid_session = UserSessionValidator().verify(session, discharge)
            if valid_session:
                context['discharge_secret'] = (
                    self._get_secret_for_discharge(discharge)
                )
        except Exception as e:
            self.logger.exception(e)
        return render_template("auth/refresh_auth.html", **context)

    def _get_secret_for_discharge(self, discharge):
        discharge_macaroon = Macaroon.from_binary(discharge)
        return self.redis.get(discharge_macaroon.identifier).decode('ascii')
