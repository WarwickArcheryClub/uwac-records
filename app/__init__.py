from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect

# Init app
app = Flask(__name__)
app.config.from_object('config')

# Init database
db = SQLAlchemy(app)

# Register custom Jinja2 filters
from app.mod_site.filters import strip_spaces

app.jinja_env.filters['strip_spaces'] = strip_spaces

# Register blueprints
from app.mod_site.controllers import mod_site as site_module
from app.mod_api.controllers import mod_api as api_module

app.register_blueprint(site_module, url_prefix='/records')
app.register_blueprint(api_module)

# Init CSRF
CsrfProtect(app)

# Create all database schemas
db.create_all()
