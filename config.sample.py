# Debug flag, turn off in production
DEBUG = True

# Database access URI for the system
SQLALCHEMY_DATABASE_URI = "engine://username:password@host/database"

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Secret key for sessions - CSRF uses the same key
SECRET_KEY = 'shh its a secret'

# Enable CSRF on all site requests
CSRF_ENABLED = True
