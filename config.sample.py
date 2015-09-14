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

# Email settings
MAIL_SERVER = 'your.smtp.server.here'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'your@email.here'
MAIL_PASSWORD = 'yourPassw0rdH3re'
