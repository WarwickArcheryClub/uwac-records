from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Init app
app = Flask(__name__)
app.config.from_object('config')

# Init database
db = SQLAlchemy(app)

# Create all database schemas
db.create_all()
