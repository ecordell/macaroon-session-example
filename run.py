import os

from app import app


def get_debug():
    val = os.environ.get('DEBUG')
    if val == 'True':
        return True
    return False


app.run(host='0.0.0.0', port=8000, debug=get_debug())
