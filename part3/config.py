"""App configuration settings."""
import os


class Config:
    """Default configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hbnb_dev.db'


class DevelopmentConfig(Config):
    """Configuration used during development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///hbnb_dev.db'


class TestingConfig(Config):
    """Configuration used for tests."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Configuration used for production deployments (MySQL by default)."""
    DEBUG = False
    db_user = os.environ.get('MYSQL_USER', 'hbnb_user')
    db_password = os.environ.get('MYSQL_PASSWORD', 'hbnb_password')
    db_host = os.environ.get('MYSQL_HOST', 'localhost')
    db_port = os.environ.get('MYSQL_PORT', '3306')
    db_name = os.environ.get('MYSQL_DATABASE', 'hbnb')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or (
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    )
