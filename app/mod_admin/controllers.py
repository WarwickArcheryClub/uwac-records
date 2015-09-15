from threading import Thread

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user
from flask_mail import Message
from app.models import Users, QueuedScores, Scores
from app import app, db, mail
import bcrypt

mod_admin = Blueprint('admin', __name__, url_prefix='/records/admin')


@mod_admin.route('/', methods=['GET'])
@login_required
def dashboard():
    return render_template('admin/dashboard.html')


@mod_admin.route('/score/<int:score_id>/approve', methods=['GET'])
@login_required
def approve_score(score_id):
    score = QueuedScores.query.get(score_id)

    if score is None:
        flash('Score doesn\'t exist', 'score')
        return redirect(url_for('.dashboard'))
    else:
        approved = Scores(score.archer_id, score.round_id, score.event_id, score.bow_type, score.category, score.score,
                          score.num_hits, score.num_golds, score.num_xs, score.date)

        db.session.add(approved)
        db.session.delete(score)
        db.session.commit()

        flash('Score approved successfully', 'score')
        return redirect(url_for('.dashboard'))


@mod_admin.route('/score/<int:score_id>/reject', methods=['GET'])
@login_required
def reject_score(score_id):
    score = QueuedScores.query.get(score_id)

    if score is None:
        flash('Score doesn\'t exist', 'score')
        return redirect(url_for('.dashboard'))
    else:
        db.session.delete(score)
        db.session.commit()

        flash('Score rejected successfully', 'score')
        return redirect(url_for('.dashboard'))


@mod_admin.route('/scores', methods=['GET'])
@login_required
def list_scores():
    return render_template('admin/scores.html')


@mod_admin.route('/scores/export', methods=['GET'])
@login_required
def export_scores():
    return render_template('admin/scores-export.html')


@mod_admin.route('/members', methods=['GET'])
@login_required
def import_members():
    return render_template('admin/members.html')


@mod_admin.route('/login', methods=['GET'])
def login():
    return render_template('admin/login.html')


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
        return render_template('admin/register.html')


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

        send_mail(user)

        flash('Added user successfully', 'submission')
        return redirect(url_for('.register'))


def send_mail(user):
    msg = Message(
        '{name} added as Admin to records system on {date}'.format(name=user.name, date=user.created),
        recipients=app.config['MAIL_SYSADMIN']
    )
    msg.html = 'A new user has been added to the records system with the name {name}. If this is no issue then ' \
               'ignore this email, otherwise please ensure the system is running with Debug turned off and that no ' \
               'extra users have access to the system.'.format(name=user.name)

    thread = Thread(target=send_async_email, args=[msg])
    thread.start()


def send_async_email(msg):
    with app.app_context():
        mail.send(msg)
