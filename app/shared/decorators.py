from functools import wraps

from flask import request, redirect, url_for

from app.service_locator import ServiceLocator
from app.shared.constants import COOKIE_KEY
from app.tokens.user_session import UserSessionValidator


def requires_session():
    def decorator(method):
        @wraps(method)
        def f(*args, **kwargs):
            return authenticate_session(method, *args, **kwargs)
        return f
    return decorator


def authenticate_session(method, *args, **kwargs):
    try:
        if COOKIE_KEY not in request.cookies:
            raise Exception('Session Not Found')

        session = request.cookies.get(COOKIE_KEY)
        valid_session = UserSessionValidator().verify(session)

        if not valid_session:
            raise Exception('Invalid Session')

        return method(*args, **kwargs)
    except Exception as e:
        ServiceLocator.get_logger().exception(e)
        return redirect(url_for('auth.login'))

