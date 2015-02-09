from flask import Flask

from app.authentication.controllers import mod_auth as auth_module
from .services import configure_services
from .errors import add_error_handlers


__all__ = [
    'AppFactory',
    'app',
]


class AppFactory:

    def __init__(self):
        self.app = Flask(__name__)

        # Load config
        self.app.config.from_object('config')
        configure_services(self.app)
        self.configure_views()

    def configure_views(self):
        self.app.register_blueprint(auth_module)
        add_error_handlers(self.app)

app = AppFactory().app
