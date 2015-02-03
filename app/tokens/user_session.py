from pymacaroons import Macaroon, Verifier
import arrow

from app.shared.constants import (
   AUTH_SERVICE_LOCATION, TARGET_SERVICE_LOCATION, TIME_KEY
)
from app.shared.functions import create_key_id_pair
from app.tokens.caveat_verifiers import verify_time
from app.service_locator import ServiceLocator

class UserSessionFactory:
    """
    This factory creates user session macaroons as the "Target Service". It is
    added to the user's cookies when they log in.
    """

    def __init__(self, username):
        self.redis = ServiceLocator.get_redis()
        self.username = username
        if not self.username:
            raise ValueError(
                'Username required to create macaroon.'
            )

    def create_macaroon(self):
        (key_id, key) = create_key_id_pair(
            prefix='{loc}::{user}::'.format(
                loc=TARGET_SERVICE_LOCATION,
                user=self.username
            )
        )
        macaroon = Macaroon(
            location=TARGET_SERVICE_LOCATION,
            key=key,
            identifier=key_id
        )
        discharge = self._add_user_caveat(macaroon)
        protected = macaroon.prepare_for_request(discharge)
        return macaroon, protected

    def create_token(self):
        macaroon, protected = self.create_macaroon()
        return '{root}::{discharge}'.format(
            root=macaroon.serialize(),
            discharge=protected.serialize()
        )

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
            AUTH_SERVICE_LOCATION,
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
        self.redis = ServiceLocator.get_redis()
        self.username = username
        if not self.username:
            raise ValueError(
                'Username required to create macaroon.'
            )

    def create_macaroon(self):
        (key_id, key) = create_key_id_pair(
            prefix='{loc}::{user}::'.format(
                loc=AUTH_SERVICE_LOCATION,
                user=self.username
            )
        )
        macaroon = Macaroon(
            location=AUTH_SERVICE_LOCATION,
            key=key,
            identifier=key_id
        )
        expires = arrow.utcnow().replace(
            minutes=1
        )
        macaroon.add_first_party_caveat(
            '{key} < {expires}'.format(
                key=TIME_KEY,
                expires=str(expires)
            )
        )
        return macaroon


class UserSessionValidator():
    def __init__(self):
        self.redis = ServiceLocator.get_redis()
        self.logger = ServiceLocator.get_logger()

    def verify(self, session):
        macaroon, discharges = self._split_macaroon_and_discharges(session)
        self.logger.debug('Root Macaroon:\n' + macaroon.inspect())
        for d in discharges:
            self.logger.debug('Discharge Macaroon:\n' + d.inspect())

        verifier = Verifier()
        verifier.satisfy_general(verify_time)
        verified = verifier.verify(
            macaroon,
            self.redis.get(macaroon.identifier),
            discharge_macaroons=discharges
        )
        return verified

    def _split_macaroon_and_discharges(self, session):
        macaroons = session.split('::')
        return (
            Macaroon.from_binary(macaroons[0]),
            [Macaroon.from_binary(m) for m in macaroons[1:]]
        )
