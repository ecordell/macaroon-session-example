import logging
import sys

from flask import g
from redis import StrictRedis


def configure_redis(app):
    @app.before_request
    def before_request():
        g.redis = StrictRedis.from_url(
            app.config['REDIS_URL']
        )


def configure_logger(app):
    out = logging.StreamHandler(sys.stdout)
    out.setLevel(logging.DEBUG)
    app.logger.addHandler(out)
    app.logger.setLevel(logging.DEBUG)


def configure_services(app):
    configure_redis(app)
    configure_logger(app)
