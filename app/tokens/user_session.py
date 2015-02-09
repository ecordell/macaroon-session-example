from pymacaroons import Macaroon, Verifier
from flask import current_app, g

from app.utils import expire_time_from_duration
from app.tokens.utils import create_key_id_pair
from app.tokens.caveat_verifiers import verify_time


class UserSessionFactory:
    """
    This factory creates user session macaroons as the "Target Service". It is
    added to the user's cookies when they log in.
    """

    def __init__(self, username):
        self.redis = g.redis
        self.username = username
        if not self.username:
            raise ValueError(
                'Username required to create macaroon.'
            )

    def create_macaroons(self):
        (key_id, key) = create_key_id_pair(
            prefix='{loc}::{user}::'.format(
                loc=current_app.config['TARGET_SERVICE_LOCATION'],
                user=self.username
            )
        )
        macaroon = Macaroon(
            location=current_app.config['TARGET_SERVICE_LOCATION'],
            key=key,
            identifier=key_id
        )
        discharge = self._add_user_caveat(macaroon)
        protected = macaroon.prepare_for_request(discharge)
        return macaroon, protected

    def create_tokens(self):
        session, discharge = self.create_macaroons()
        return session.serialize(), session.signature, discharge.serialize()

    def _add_user_caveat(self, macaroon):
        """
        Adds a third party caveat requiring that the user be authenticated with
        auth_service.localhost. Also creates a corresponding discharge macaroon
        and returns it. (This only makes sense to do since the auth and target
        service are the same)
        """
        discharge = UserDischargeFactory(self.username).create_macaroon()
        key_id = discharge.identifier
        macaroon.add_third_party_caveat(
            current_app.config['AUTH_SERVICE_LOCATION'],
            self.redis.get(key_id),
            key_id
        )
        return discharge


class UserDischargeFactory:
    """
    This factory creates discharge macaroons as the "Authenication Service"
    This is bound to the session macaroon and added to the session cookie when
    logging in. It is then refreshed through local communication with an iframe
    which holds the caveat root key for the discharge.
    """

    def __init__(self, username):
        self.redis = g.redis
        self.username = username
        if not self.username:
            raise ValueError(
                'Username required to create macaroon.'
            )

    def create_macaroon(self):
        (key_id, key) = create_key_id_pair(
            prefix='{loc}::{user}::'.format(
                loc=current_app.config['AUTH_SERVICE_LOCATION'],
                user=self.username
            ),
            duration=current_app.config['MAX_SESSION_REFRESH_LENGTH']
        )
        macaroon = Macaroon(
            location=current_app.config['AUTH_SERVICE_LOCATION'],
            key=key,
            identifier=key_id
        )
        expires = expire_time_from_duration(
            current_app.config['SESSION_LENGTH']
        )
        macaroon.add_first_party_caveat(
            '{key} < {expires}'.format(
                key=current_app.config['TIME_KEY'],
                expires=str(expires)
            )
        )
        return macaroon


class UserSessionValidator():
    def __init__(self):
        self.redis = g.redis
        self.logger = current_app.logger

    def verify(self, session, discharge):
        session_macaroon = Macaroon.from_binary(session)
        discharge_macaroon = Macaroon.from_binary(discharge)

        self.logger.debug('Root Macaroon:\n' + session_macaroon.inspect())
        self.logger.debug('Discharge Macaroon:\n' + discharge_macaroon.inspect())

        verifier = Verifier()
        verifier.satisfy_general(verify_time)
        verified = verifier.verify(
            session_macaroon,
            self.redis.get(session_macaroon.identifier),
            discharge_macaroons=[discharge_macaroon]
        )
        return verified
