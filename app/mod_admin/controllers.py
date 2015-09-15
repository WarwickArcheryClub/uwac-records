from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user
from app.models import Users
from app import app, db

import bcrypt

mod_admin = Blueprint('admin', __name__, url_prefix='/admin')


@mod_admin.route('/', methods=['GET'])
@login_required
def dashboard():
    return 'Hello, world!'


@mod_admin.route('/login', methods=['GET'])
def login():
    return render_template('/admin/login.html')


@mod_admin.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        if not request.form['username'] or \
                not request.form['password']:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('.login'))
    except KeyError:
        flash('Please fill in all fields', 'error')
        return redirect(url_for('.login'))

    user = Users.query.filter(Users.name == request.form['username']).first()

    if user is None:
        flash('Invalid username or password', 'error')
        return redirect(url_for('.login'))

    if bcrypt.hashpw(request.form['password'].encode(), user.password) == user.password:
        login_user(user)
        return redirect(url_for('.dashboard'))
    else:
        flash('Invalid username or password', 'error')
        return redirect(url_for('.login'))


@mod_admin.route('/register', methods=['GET'])
def register():
    if not app.config['DEBUG']:
        return redirect(url_for('.login'))
    else:
        return render_template('/admin/register.html')


@mod_admin.route('/register/new', methods=['POST'])
def new_user():
    if not app.config['DEBUG']:
        return redirect(url_for('.login'))
    else:
        try:
            if not request.form['username'] or \
                    not request.form['password']:
                flash('Please fill in all fields', 'submission')
                return redirect(url_for('.login'))
        except KeyError:
            flash('Please fill in all fields', 'submission')
            return redirect(url_for('.login'))

        user = Users(request.form['username'], bcrypt.hashpw(request.form['password'].encode('utf-8'),
                                                             bcrypt.gensalt()))

        db.session.add(user)
        db.session.commit()

        flash('Added user successfully', 'submission')
        return redirect(url_for('.register'))
