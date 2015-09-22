from threading import Thread
from time import strptime, mktime
from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, current_user, logout_user
from flask_mail import Message
from app.mod_site.controllers import is_integer, is_date, is_category, category_map
from app.models import Users, QueuedScores, Scores, NewArchers, Archers, BowTypes, Rounds, Events
from app import app, db, mail
from genderize import Genderize
import requests
import bcrypt




# Use the C ElementTree implementation where possible
try:
    from xml.etree.cElementTree import ElementTree, fromstring
except ImportError:
    from xml.etree.ElementTree import ElementTree, fromstring

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


@mod_admin.route('/score/add', methods=['GET'])
def add_score():
    return render_template('admin/score-add.html', bow_types=BowTypes.query.order_by(db.desc(BowTypes.id)).all())


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


@mod_admin.route('/scores/queued', methods=['GET'])
@login_required
def approve_scores():
    return render_template('admin/scores-approve.html', scores=QueuedScores.query.all())


@mod_admin.route('/scores/queued/update', methods=['POST'])
@login_required
def update_score_status():
    updated_count = 0

    for item in request.form.iteritems():
        score_id, status = item

        if 'csrf_token' in score_id:
            continue

        score = QueuedScores.query.get(score_id)

        if not score:
            continue

        if 'A' in status:
            db.session.add(Scores(score.archer_id, score.round_id, score.event_id, score.bow_type, score.category,
                                  score.score, score.num_hits, score.num_golds, score.num_xs, score.date))
            db.session.delete(score)

            updated_count += 1
        elif 'R' in status:
            db.session.delete(score)

            updated_count += 1
        else:
            continue

    db.session.commit()

    if updated_count > 0:
        flash('{num} scores{s} updated successfully'.format(num=updated_count, s='s' if updated_count > 1 else ''),
              'submission')

    return redirect(url_for('.approve_scores'))


@mod_admin.route('/score/<int:score_id>/edit', methods=['GET'])
@login_required
def edit_score(score_id):
    score = Scores.query.get(score_id)

    if not score:
        return redirect(url_for('.dashboard'))

    try:
        next_url = request.args['next']
    except KeyError:
        next_url = url_for('.dashboard')

    return render_template('admin/score-edit.html', score=score, next=next_url, bow_types=BowTypes.query.all())


@mod_admin.route('/score/update', methods=['POST'])
@login_required
def update_score():
    try:
        if not request.form['bow-select'] or \
                not request.form['archer-select'] or \
                not request.form['round-select'] or \
                not request.form['event-select'] or \
                not request.form['category-select'] or \
                not request.form['date-input'] or \
                not request.form['score-hits'] or \
                not request.form['score-score'] or \
                not request.form['score-golds'] or \
                not request.form['score-id'] or \
                not request.form['origin']:
            flash('Incomplete score', 'submission')
            return redirect(request.form['origin'])
    except KeyError:
        flash('Incomplete score', 'submission')
        return redirect(url_for('.dashboard'))

    if 'score-xs' in request.form:
        if not request.form['score-xs']:
            flash('Incomplete score', 'submission')
            return redirect(request.form['origin'])

    if not is_integer(request.form['bow-select']) or \
            not is_integer(request.form['archer-select']) or \
            not is_integer(request.form['round-select']) or \
            not is_integer(request.form['event-select']) or \
            not is_category(request.form['category-select']) or \
            not is_date(request.form['date-input']) or \
            not is_integer(request.form['score-hits']) or \
            not is_integer(request.form['score-score']) or \
            not is_integer(request.form['score-golds']) or \
            not is_integer(request.form['score-id']):
        flash('Unexpected score information type', 'submission')
        return redirect(request.form['origin'])

    if 'score-xs' in request.form:
        if not is_integer(request.form['score-xs']):
            flash('Unexpected score information type', 'submission')
            return redirect(request.form['origin'])

    if not db.session.query(db.exists().where(Archers.id == request.form['archer-select'])).scalar():
        flash('Archer doesn\'t exist', 'submission')
        return redirect(request.form['origin'])
    archer = Archers.query.get(request.form['archer-select'])

    if not db.session.query(db.exists().where(Rounds.id == request.form['round-select'])).scalar():
        flash('Round doesn\'t exist', 'submission')
        return redirect(request.form['origin'])
    score_round = Rounds.query.get(request.form['round-select'])

    if not db.session.query(db.exists().where(Events.id == request.form['event-select'])).scalar():
        flash('Event doesn\'t exist', 'submission')
        return redirect(request.form['origin'])
    event = Events.query.get(request.form['event-select'])

    if not db.session.query(db.exists().where(BowTypes.id == request.form['bow-select'])).scalar():
        flash('Bow type doesn\'t exist', 'submission')
        return redirect(request.form['origin'])
    bow_type = BowTypes.query.get(request.form['bow-select'])

    if int(request.form['score-hits']) not in range(0, score_round.max_hits + 1):
        flash('Incorrect number of hits', 'submission')
        return redirect(request.form['origin'])
    hits = int(request.form['score-hits'])

    if int(request.form['score-golds']) not in range(0, score_round.max_hits + 1):
        flash('Incorrect number of golds', 'submission')
        return redirect(request.form['origin'])
    golds = int(request.form['score-golds'])

    if 'score-xs' in request.form:
        if int(request.form['score-xs']) not in range(0, golds + 1):
            flash('Incorrect number of Xs', 'submission')
            return redirect(request.form['origin'])
        else:
            if score_round.r_type is 'Clout' or 'Indoors' in score_round.r_type:
                xs = None
            else:
                xs = int(request.form['score-xs'])
    else:
        if score_round.r_type is 'Clout' or 'Indoors' in score_round.r_type:
            xs = None
        else:
            xs = 0

    if int(request.form['score-score']) not in range(0, score_round.max_score + 1):
        flash('Incorrect score', 'submission')
        return redirect(request.form['origin'])
    score = int(request.form['score-score'])

    category = category_map(request.form['category-select'])
    score_date = date.fromtimestamp(mktime(strptime(request.form['date-input'], '%Y-%m-%d')))

    try:
        new_score = 'new' in request.form['score-status']
    except KeyError:
        new_score = False

    if new_score:
        score_obj = Scores(archer.id, score_round.id, event.id, bow_type.id, category, score, hits, golds, xs,
                           score_date)

        db.session.add(score_obj)

        flash('Added new score successfully', 'submission')
    else:
        old_score = Scores.query.get(int(request.form['score-id']))

        if not old_score:
            flash('Original score doesn\'t exist', 'submission')
            return redirect(request.form['origin'])

        old_score.archer_id = archer.id
        old_score.round_id = score_round.id
        old_score.event_id = event.id
        old_score.bow_type = bow_type.id
        old_score.category = category
        old_score.score = score
        old_score.num_hits = hits
        old_score.num_golds = golds
        old_score.num_xs = xs
        old_score.date = score_date

        flash('Updated score successfully', 'submission')

    db.session.commit()

    if new_score:
        return redirect(url_for('admin.add_score'))
    else:
        try:
            return redirect(request.form['origin'])
        except KeyError:
            return redirect(url_for('.dashboard'))


@mod_admin.route('/score/<int:score_id>/delete', methods=['GET'])
@login_required
def delete_score(score_id):
    score = Scores.query.get(score_id)

    if not score:
        try:
            flash('Score doesn\'t exist', 'submission')
            return redirect(request.args['next'])
        except KeyError:
            return redirect(url_for('.dashboard'))

    db.session.delete(score)
    db.session.commit()

    flash('Score successfully deleted', 'submission')

    try:
        return redirect(request.args['next'])
    except KeyError:
        return redirect(url_for('.dashboard'))


@mod_admin.route('/scores/export', methods=['GET'])
@login_required
def export_scores():
    return render_template('admin/scores-export.html')


@mod_admin.route('/members/import', methods=['GET'])
@login_required
def import_members():
    xml_request = requests.get(app.config['WS_API_ENDPOINT'])

    root_element = fromstring(xml_request.text.encode('utf-8'))

    new_archers = []

    for child in root_element:
        f_name = unicode(child.find('FirstName').text.title(), 'utf-8')
        l_name = unicode(child.find('LastName').text.title(), 'utf-8')
        try:
            card_num = unicode(child.find('UniqueID').text, 'utf-8')
        except TypeError:
            card_num = None

        try:
            email = unicode(child.find('EmailAddress').text, 'utf-8')
        except TypeError:
            email = None

        archer = NewArchers(f_name, l_name, email, card_num)

        if card_num:
            if Archers.query.filter(Archers.card_number == archer.card_number).first():
                continue
            elif NewArchers.query.filter(NewArchers.card_number == archer.card_number).first():
                continue
        else:
            if Archers.query.filter(Archers.first_name.like(archer.first_name)).filter(
                    Archers.last_name.like(archer.last_name)).first():
                continue
            elif NewArchers.query.filter(NewArchers.first_name.like(archer.first_name)).filter(
                    NewArchers.last_name.like(archer.last_name)).first():
                continue

        new_archers.append(archer)

    genderize = Genderize()

    for chunk in chunks(new_archers, 10):
        result = zip(chunk, genderize.get(map(get_first_name, chunk)))
        for item in result:
            new_archer, gender = item
            try:
                if float(gender['probability']) >= 0.5:
                    assigned = Archers(new_archer.first_name, new_archer.last_name,
                                       'M' if u'male' in gender['gender'] else 'F', new_archer.email,
                                       new_archer.card_number, None)
                    db.session.add(assigned)
                else:
                    db.session.add(new_archer)
            except KeyError:
                db.session.add(new_archer)

    db.session.commit()

    need_assignment = NewArchers.query.all()

    return render_template('admin/members-import.html', archers=need_assignment)


@mod_admin.route('/members/import/update', methods=['POST'])
@login_required
def update_members():
    assigned_count = 0

    for item in request.form.iteritems():
        archer_id, gender = item

        if 'csrf_token' in archer_id:
            continue

        archer = NewArchers.query.filter(NewArchers.card_number == unicode(archer_id, 'utf-8')).first()

        if not archer:
            continue

        assigned = Archers(archer.first_name, archer.last_name, gender, archer.email, archer.card_number, None)

        db.session.add(assigned)
        db.session.delete(archer)

        assigned_count += 1

    db.session.commit()

    if assigned_count > 0:
        flash('{num} gender{s} entered successfully'.format(num=assigned_count, s='s' if assigned_count > 1 else ''),
              'submission')

    return redirect(url_for('.import_members'))


@mod_admin.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard'))

    return render_template('admin/login.html')


@mod_admin.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()

    return redirect(url_for('site.home'))


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
        try:
            remember = True if request.form['remember-me'] == '1' else False
        except KeyError:
            remember = False

        login_user(user, remember=remember)

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


def get_first_name(item):
    if type(item) is NewArchers:
        return item.first_name
    else:
        return None


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]
