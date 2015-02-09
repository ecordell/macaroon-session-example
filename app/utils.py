from flask import current_app
from isodate import parse_duration
import arrow


def expire_time_from_duration(duration_string):
    duration = parse_duration(duration_string)
    expires = arrow.utcnow().replace(
        seconds=duration.seconds,
        days=duration.days
    )
    return expires


def get_session_and_discharge(request):
    session = request.cookies.get(current_app.config['SESSION_COOKIE_KEY'])
    discharge = request.cookies.get('auth_discharge')
    return session, discharge
