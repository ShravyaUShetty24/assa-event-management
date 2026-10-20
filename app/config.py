"""
ASSA Event Manager — Configuration
"""

import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()

    # Default to SQLite if DATABASE_URL is not set (no installation needed)
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///assa.db')
    SQLALCHEMY_DATABASE_URI = _db_url

    # SQLite needs check_same_thread=False for Flask's multi-threaded dev server
    SQLALCHEMY_ENGINE_OPTIONS = (
        {'connect_args': {'check_same_thread': False}}
        if _db_url.startswith('sqlite')
        else {}
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    LOAD_ML_MODELS = os.environ.get('LOAD_ML_MODELS', '1') == '1'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
