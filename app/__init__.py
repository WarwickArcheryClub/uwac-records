from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Init app
app = Flask(__name__)
app.config.from_object('config')

# Init database
db = SQLAlchemy(app)

from app.mod_site.controllers import mod_site as site_module

app.register_blueprint(site_module)

# Create all database schemas
db.create_all()
