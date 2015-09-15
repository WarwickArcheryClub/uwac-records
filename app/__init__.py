from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CsrfProtect

# Init app
app = Flask(__name__)
app.config.from_object('config')

# Init database
db = SQLAlchemy(app)

# Init mail server
mail = Mail(app)

# Register custom Jinja2 filters
from app.mod_site.filters import strip_spaces
from app.mod_site.filters import expand_gender

app.jinja_env.filters['strip_spaces'] = strip_spaces
app.jinja_env.filters['expand_gender'] = expand_gender

# Register custom URL converters

from app.mod_site.converters import DateConverter

app.url_map.converters['date'] = DateConverter

# Register blueprints
from app.mod_site.controllers import mod_site as site_module
from app.mod_api.controllers import mod_api as api_module

app.register_blueprint(site_module, url_prefix='/records')
app.register_blueprint(api_module)

# Init CSRF
CsrfProtect(app)

# Create all database schemas
db.create_all()
