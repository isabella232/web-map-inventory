import logging

from flask import Flask
from flask_dotenv import DotEnv


class Config:
    DEBUG = False
    TESTING = False

    @classmethod
    def init_app(cls, app: Flask):
        env = DotEnv()
        env.init_app(app)


class ProductionConfig(Config):
    ENV = 'production'
    LOGGING_LEVEL = logging.WARNING


class DevelopmentConfig(Config):
    ENV = 'development'
    LOGGING_LEVEL = logging.INFO


class TestConfig(Config):
    ENV = 'testing'

    DEBUG = True
    TESTING = True

    LOGGING_LEVEL = logging.DEBUG


config = {
    'testing': TestConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
