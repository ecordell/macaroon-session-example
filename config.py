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
