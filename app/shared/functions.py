import os
import binascii

from app.shared.constants import COOKIE_KEY, SECRET_LENGTH, ID_LENGTH
from flask import current_app
from isodate import parse_duration
import arrow


def get_config(key, default=None):
    """
    Get settings from environment if exists,
    return default value otherwise

    example:

    ADMIN_EMAIL = get_config('ADMIN_EMAIL', 'default@email.com')
    """
    val = os.environ.get(key, default)
    if val == 'True':
        val = True
    elif val == 'False':
        val = False
    return val


def expire_time_from_duration(duration_string):
    duration = parse_duration(duration_string)
    expires = arrow.utcnow().replace(
        seconds=duration.seconds,
        days=duration.days
    )
    return expires


def set_session_cookie(
    response, session_macaroon, session_signature, auth_discharge
):
    response.set_cookie(
        COOKIE_KEY,
        value=session_macaroon,
        max_age=None,
        expires=None,
        path='/',
        domain=None,
        secure=False,
        httponly=True
    )
    response.set_cookie(
        'session_signature',
        value=session_signature,
        max_age=None,
        expires=None,
        path='/',
        domain=None,
        secure=False,
        httponly=False
    )
    response.set_cookie(
        'auth_discharge',
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
        'max_refresh_time',
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


def get_session_and_discharge(request):
    session = request.cookies.get(COOKIE_KEY)
    discharge = request.cookies.get('auth_discharge')
    return session, discharge


def create_key_id_pair(prefix=None, duration=None):
    from app.service_locator import ServiceLocator
    if not prefix:
        prefix = ''
    secret_key = binascii.hexlify(os.urandom(SECRET_LENGTH)).decode('ascii')
    secret_key_id = prefix + binascii.hexlify(os.urandom(ID_LENGTH)).decode('ascii')
    redis = ServiceLocator.get_redis()
    redis.set(secret_key_id, secret_key)
    if duration:
        expires = parse_duration(duration).total_seconds()
        redis.expire(secret_key_id, int(expires))
    return secret_key_id, secret_key
