import os
import binascii

from flask import current_app, g
from isodate import parse_duration


def create_key_id_pair(prefix=None, duration=None):
    if not prefix:
        prefix = ''
    secret_key = binascii.hexlify(
        os.urandom(current_app.config['SECRET_LENGTH'])
    ).decode('ascii')
    secret_key_id = prefix + binascii.hexlify(
        os.urandom(current_app.config['ID_LENGTH'])
    ).decode('ascii')
    g.redis.set(secret_key_id, secret_key)
    if duration:
        expires = parse_duration(duration).total_seconds()
        g.redis.expire(secret_key_id, int(expires))
    return secret_key_id, secret_key
