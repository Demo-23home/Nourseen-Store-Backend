"""
NourseenStore — Development Settings
"""
from .base import *
from decouple import config, Csv

DEBUG = True

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Detailed error pages
INSTALLED_APPS += []

# Disable throttling in development for easier testing
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
