import logging
import sys

from redis import StrictRedis

from app.shared.functions import get_config


class ServiceLocator:
    redis = None

    @classmethod
    def get_redis(cls):
        if not cls.redis:
            cls.redis = StrictRedis.from_url(
                get_config('REDIS_URL', '')
            )
        return cls.redis

    @classmethod
    def get_logger(cls):
        logger = logging.getLogger('iam')
        if not logger.handlers:
            out = logging.StreamHandler(sys.stdout)
            logger.addHandler(out)
            logger.setLevel(logging.DEBUG)
        return logger
