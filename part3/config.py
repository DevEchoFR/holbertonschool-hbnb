"""App configuration settings."""


class Config:
    """Default configuration."""
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Configuration used during development."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration used for tests."""
    TESTING = True
    DEBUG = True
