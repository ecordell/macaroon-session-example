import os
import binascii

from app.shared.constants import COOKIE_KEY, SECRET_LENGTH, ID_LENGTH
from app.service_locator import ServiceLocator

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


def set_session_cookie(response, session_token):
    response.set_cookie(
        COOKIE_KEY,
        value=session_token,
        max_age=None,
        expires=None,
        path='/',
        domain=None,
        secure=False,
        httponly=True
    )


def create_key_id_pair(prefix=None):
    if not prefix:
        prefix = ''
    secret_key = binascii.hexlify(os.urandom(SECRET_LENGTH)).decode('ascii')
    secret_key_id = prefix + binascii.hexlify(os.urandom(ID_LENGTH)).decode('ascii')
    ServiceLocator.get_redis().set(secret_key_id, secret_key)
    return secret_key_id, secret_key
