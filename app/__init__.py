from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CsrfProtect
from flask_login import LoginManager

# Init app
app = Flask(__name__)
app.config.from_object('config')

# Init login manager
login = LoginManager()
login.init_app(app)
login.login_view = '/records/admin/login'

# Init database
db = SQLAlchemy(app)

# Init mail server
mail = Mail(app)

# Register custom Jinja2 filters
from app.mod_site.filters import id_escape
from app.mod_site.filters import expand_gender

app.jinja_env.filters['strip_spaces'] = id_escape
app.jinja_env.filters['expand_gender'] = expand_gender

# Register custom URL converters

from app.mod_site.converters import DateConverter

app.url_map.converters['date'] = DateConverter

# Register blueprints
from app.mod_admin.controllers import mod_admin as admin_module
from app.mod_site.controllers import mod_site as site_module
from app.mod_api.controllers import mod_api as api_module

app.register_blueprint(admin_module)
app.register_blueprint(site_module)
app.register_blueprint(api_module)

# Init CSRF
CsrfProtect(app)

# Create all database schemas
db.create_all()
