import os

# Debug flag, turn off in production
DEBUG = True

# Database access URI for the system
SQLALCHEMY_DATABASE_URI = "engine://username:password@host/database"

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Secret key for sessions - CSRF uses the same key
SECRET_KEY = 'shh its a secret'

# Enable CSRF on all site requests
CSRF_ENABLED = True

# Login session strength
SESSION_PROTECTION = 'strong'

# Base URL for use in link construction
SITE_URL = 'yourclubsweb.site'

# Sport club members API endpoint
WS_API_ENDPOINT = 'http://sportsclub.api/endpoint/here'

# Email settings
MAIL_SERVER = 'your.smtp.server.here'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'your@email.here'
MAIL_PASSWORD = 'yourPassw0rdH3re'
MAIL_RECORDS = ['records@yourclub.email']
MAIL_SYSADMIN = ['sysadmin@yourclub.email']

# Default sender address (optional)
# MAIL_DEFAULT_SENDER = 'new-record@yourclub.email'
