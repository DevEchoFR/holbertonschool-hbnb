import os

class Config:
    DEBUG = os.getenv("DEBUG", "1") == "1"