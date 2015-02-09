import os

# Server settings
# ---------------------------------------------------------
# Settings for configuring flask

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
THREADS_PER_PAGE = int(os.environ.get('THREADS_PER_PAGE', 2))
CSRF_ENABLED = True
CSRF_SESSION_KEY = os.environ.get('CSRF_SESSION_KEY', "default_secret_csrf")
SECRET_KEY = os.environ.get('SECRET_KEY', "default_secret_key")
SERVER_NAME = os.environ.get('SERVER_NAME', 'localhost')
AUTH_ORIGIN = os.environ.get('AUTH_ORIGIN', 'localhost')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379')
SESSION_LENGTH = os.environ.get('SESSION_LENGTH', 'PT15M')
MAX_SESSION_REFRESH_LENGTH = os.environ.get(
    'MAX_SESSION_REFRESH_LENGTH', 'PT3H'
)

# Constants
SESSION_COOKIE_KEY = 'macaroon_session'
AUTH_REFRESH_DISCHARGE_KEY = 'auth_discharge'
SESSION_SIGNATURE_KEY = 'session_signature'
MAX_SESSION_REFRESH_KEY = 'max_refresh_time'
TIME_KEY = 'time'
SECRET_LENGTH = 32
ID_LENGTH = 16

AUTH_SERVICE_LOCATION = 'auth_service.localhost'
TARGET_SERVICE_LOCATION = 'target_service.localhost'
