import arrow

__all__ = [
    'verify_time',
]


def verify_time(caveat):
    if not caveat.startswith('time < '):
        return False
    try:
        now = arrow.utcnow()
        when = arrow.get(caveat[7:])
        return now < when
    except:
        return False
