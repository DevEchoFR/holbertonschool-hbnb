"""App configuration settings."""
import os


class Config:
    """Default configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'


class DevelopmentConfig(Config):
    """Configuration used during development."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration used for tests."""
    TESTING = True
    DEBUG = True
