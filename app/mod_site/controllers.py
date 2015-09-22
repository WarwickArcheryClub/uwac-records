import json
from time import strptime, mktime
from datetime import date
from threading import Thread

import Levenshtein as lev
from flask import Blueprint, render_template, request, redirect, flash, url_for, abort
from app.models import IndividualRecords, BowTypes, db, Archers, Scores, Classifications, Rounds, Events, QueuedScores
from app import mail, app
from flask_mail import Message

mod_site = Blueprint('site', __name__, url_prefix='/records')


@mod_site.route('/', methods=['GET'])
def home():
    indoor_categories_shot = db.session.query(IndividualRecords.bow_type.distinct().label('bow_type')).filter(
        db.or_(IndividualRecords.round_type == 'Indoors', IndividualRecords.round_type == 'WA Indoors')).order_by(
        db.desc(IndividualRecords.bow_type)).all()
    indoor_categories = []

    for cat in indoor_categories_shot:
        category = {
            'name': cat.bow_type,
            'scores': IndividualRecords.query.filter(db.or_(IndividualRecords.round_type == 'Indoors',
                                                            IndividualRecords.round_type == 'WA Indoors')).filter(
                IndividualRecords.bow_type == cat.bow_type).order_by(IndividualRecords.round_name,
                                                                     db.desc(IndividualRecords.category),
                                                                     db.desc(IndividualRecords.score),
                                                                     db.desc(IndividualRecords.num_golds)).all()
        }

        indoor_categories.append(category)

    outdoor_categories_shot = db.session.query(
        IndividualRecords.bow_type.distinct().label('bow_type')).filter(
        db.not_(
            db.or_(IndividualRecords.round_type == 'Indoors', IndividualRecords.round_type == 'WA Indoors'))).order_by(
        db.desc(IndividualRecords.bow_type)).all()
    outdoor_categories = []

    for cat in outdoor_categories_shot:
        category = {
            'name': cat.bow_type,
            'scores': IndividualRecords.query.filter(db.not_(db.or_(IndividualRecords.round_type == 'Indoors',
                                                                    IndividualRecords.round_type == 'WA Indoors'))).filter(
                IndividualRecords.bow_type == cat.bow_type).order_by(IndividualRecords.round_name,
                                                                     db.desc(IndividualRecords.category),
                                                                     db.desc(IndividualRecords.score),
                                                                     db.desc(IndividualRecords.num_golds)).all()
        }

        outdoor_categories.append(category)

    bow_types = BowTypes.query.order_by(db.desc(BowTypes.name)).all()

    return render_template('site/search.html', bow_types=bow_types, indoor_categories=indoor_categories,
                           outdoor_categories=outdoor_categories)


@mod_site.route('/submit', methods=['POST'])
def submit():
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
                not request.form['origin']:
            flash('Incomplete score', 'submission')
            return redirect(request.form['origin'])
    except KeyError:
        flash('Incomplete score', 'submission')
        return redirect('/records/')

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
            not is_integer(request.form['score-golds']):
        flash('Incorrect score information', 'submission')
        return redirect(request.form['origin'])

    if 'score-xs' in request.form:
        if not is_integer(request.form['score-xs']):
            flash('Incorrect score information', 'submission')
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

    score_obj = QueuedScores(archer.id, score_round.id, event.id, bow_type.id, category, score, hits, golds, xs,
                             score_date)

    db.session.add(score_obj)
    db.session.commit()

    send_email(score_obj)

    flash('Score submitted successfully', 'submission')

    return redirect(request.form['origin'])


def send_email(score):
    msg = Message(
        'New score submitted by {name}'.format(name=score.archer.get_name()),
        recipients=app.config['MAIL_RECORDS']
    )
    msg.html = '{name} has submitted a score:<br/><br/>' \
               '{round} on {date} as {category}<br/>' \
               'Score: {score}, hits: {hits}, golds: {golds}, Xs: {xs}<br/><br/>' \
               'CSV format:<br/>' \
               '<pre>{name_csv},{cat_csv},{bow_csv},{round_csv},{date_csv},{event_csv},{score_csv},{hits_csv},' \
               '{golds_csv},{xs_csv},</pre><br/>' \
               'To approve the score click <a href="{approve}">here</a> or to reject click ' \
               '<a href="{reject}">this link</a><br/><br/>' \
               'This email was automatically generated, please don\'t reply.' \
        .format(name=score.archer.get_name(), round=score.round.name, date=date.strftime(score.date, '%d/%m/%Y'),
                category=score.category, score=score.score, hits=score.num_hits, golds=score.num_golds,
                xs=score.num_xs or 'N/A', name_csv=score.archer.get_name(),
                cat_csv=condense_category(score.archer.gender, score.category), bow_csv=score.bow.name,
                round_csv=score.round.name, date_csv=date.strftime(score.date, '%d/%m/%Y'), event_csv=score.event.name,
                score_csv=score.score, hits_csv=score.num_hits, golds_csv=score.num_golds, xs_csv=score.num_xs or '',
                approve=app.config['SITE_URL'] + url_for('admin.approve_score', score_id=score.id),
                reject=app.config['SITE_URL'] + url_for('admin.reject_score', score_id=score.id))

    thread = Thread(target=send_async_email, args=[msg])
    thread.start()


def send_async_email(msg):
    with app.app_context():
        mail.send(msg)


def condense_category(gender, experience):
    if experience in 'Experienced':
        if gender in 'M':
            return 'ME'
        elif gender in 'F':
            return 'FE'
        else:
            return None
    elif experience in 'Novice':
        if gender in 'M':
            return 'MN'
        elif gender in 'F':
            return 'FN'
        else:
            return None
    else:
        return None


@mod_site.route('/search', methods=['POST'])
def search():
    if request.form['search_data']:
        data = json.loads(request.form['search_data'])
        if not data['data']:
            return abort(400)
        else:
            s_type = data['data']['s_type']
            s_id = data['data']['id']
            if not s_type or not s_id:
                return abort(400)
            else:
                return redirect('/records/{}/{}'.format(s_type, s_id))
    else:
        query = request.form['search']

        if not query:
            return redirect('/records/400')

        archers = sorted(
            Archers.query.filter((Archers.first_name + u' ' + Archers.last_name).ilike(u'%{}%'.format(query))).all(),
            key=get_key,
            cmp=lambda x, y: lev.distance(x.lower(), query.lower()) - lev.distance(y.lower(), query.lower()))
        rounds = sorted(Rounds.query.filter(Rounds.name.ilike(u'%{}%'.format(query))).all(), key=get_key,
                        cmp=lambda x, y: lev.distance(x.lower(), query.lower()) - lev.distance(y.lower(),
                                                                                               query.lower()))
        events = sorted(Events.query.filter(Events.name.ilike(u'%{}%'.format(query))).all(), key=get_key,
                        cmp=lambda x, y: lev.distance(x.lower(), query.lower()) - lev.distance(y.lower(),
                                                                                               query.lower()))

        bow_types = BowTypes.query.order_by(db.desc(BowTypes.name)).all()

        return render_template('site/search-clarify.html', query=query, archers=archers, rounds=rounds, events=events,
                               bow_types=bow_types)


@mod_site.route('/event/<int:event_id>')
def event_by_id(event_id):
    event = Events.query.get_or_404(event_id)
    categories_shot = db.session.query(Scores.date.distinct().label('date')).filter(
        Scores.event_id == event_id).order_by(db.desc(Scores.date)).all()
    categories = []
    for cat in categories_shot:
        category = {
            'date': cat.date
        }
        categories.append(category)

    bow_types = BowTypes.query.order_by(db.desc(BowTypes.name)).all()

    return render_template('site/event.html', event=event, categories=categories, bow_types=bow_types)


@mod_site.route('/event/<int:event_id>/<date:event_date>')
def event_by_id_date(event_id, event_date):
    event = Events.query.get_or_404(event_id)
    categories_shot = db.session.query(Scores.round_id.distinct().label('round_id'), Scores.bow_type.label('bow_type'),
                                       (Rounds.name + ' ' + BowTypes.name).label('div_name')).join(Scores.round).join(
        Scores.bow).filter(Scores.event_id == event_id).filter(Scores.date == event_date).order_by(
        db.desc(Scores.bow_type)).all()
    categories = []
    for cat in categories_shot:
        category = {
            'round_id': cat.round_id,
            'bow_type': cat.bow_type,
            'div_name': cat.div_name,
            'scores': Scores.query.filter(Scores.round_id == cat.round_id).filter(
                Scores.bow_type == cat.bow_type).filter(Scores.event_id == event_id).filter(Scores.date == event_date)
                .order_by(db.desc(Scores.score)).order_by(db.desc(Scores.num_hits)).order_by(
                db.desc(Scores.num_golds)).order_by(db.desc(Scores.num_xs)).all(),
            'max_score': Rounds.query.get(cat.round_id).max_score
        }

        for score in category['scores']:
            gender = Archers.query.get(score.archer_id).gender
            classification = Classifications.query.get((score.round_id, score.bow_type, gender))
            score.classification = classification.get_class(score.score,
                                                            score.round.r_type) if classification is not None else None

        categories.append(category)

    bow_types = BowTypes.query.order_by(db.desc(BowTypes.name)).all()

    return render_template('site/event-detail.html', event=event, date=event_date.strftime('%Y-%m-%d'),
                           categories=categories, bow_types=bow_types)


@mod_site.route('/round/<int:round_id>')
def round_by_id(round_id):
    score_round = Rounds.query.get_or_404(round_id)
    categories_shot = db.session.query(Scores.bow_type.distinct().label('bow_type'), Archers.gender.label('gender'),
                                       (Archers.gender + ' ' + BowTypes.name).label('div_name')).filter(
        Scores.round_id == round_id).join(Scores.archer).join(Scores.bow).order_by(db.desc(Scores.bow_type)).order_by(
        Archers.gender).all()
    categories = []
    for cat in categories_shot:
        category = {
            'bow_type': cat.bow_type,
            'div_name': cat.div_name,
            'scores': Scores.query.filter(Scores.round_id == round_id).filter(Scores.bow_type == cat.bow_type).filter(
                Archers.gender == cat.gender).join(Scores.archer).order_by(db.desc(Scores.score)).order_by(
                db.desc(Scores.num_hits)).order_by(db.desc(Scores.num_golds)).order_by(db.desc(Scores.num_xs)).all(),
            'max_score': score_round.max_score
        }

        for score in category['scores']:
            classification = Classifications.query.get((score.round_id, score.bow_type, cat.gender))
            score.classification = classification.get_class(score.score,
                                                            score.round.r_type) if classification is not None else None

        categories.append(category)

    bow_types = BowTypes.query.order_by(db.desc(BowTypes.name)).all()

    return render_template('site/round.html', score_round=score_round, categories=categories, bow_types=bow_types)


@mod_site.route('/archer/<int:archer_id>')
def archer_by_id(archer_id):
    archer = Archers.query.get_or_404(archer_id)
    categories_shot = db.session.query(Scores.round_id.distinct().label('round_id'), Scores.bow_type.label('bow_type'),
                                       (Rounds.name + u' ' + BowTypes.name).label('div_name')).filter(
        Scores.archer_id == archer_id).join(Scores.bow).join(Scores.round).order_by('div_name').all()
    categories = []
    for cat in categories_shot:
        category = {
            'round_id': cat.round_id,
            'bow_type': cat.bow_type,
            'div_name': cat.div_name,
            'scores': Scores.query.filter(Scores.archer_id == archer_id).filter(Scores.round_id == cat.round_id).filter(
                Scores.bow_type == cat.bow_type).order_by(db.desc(Scores.score)).order_by(
                db.desc(Scores.num_hits)).order_by(db.desc(Scores.num_golds)).order_by(db.desc(Scores.num_xs)).all(),
            'max_score': Rounds.query.get(cat.round_id).max_score
        }

        for score in category['scores']:
            classification = Classifications.query.get((score.round_id, score.bow_type, archer.gender))
            score.classification = classification.get_class(score.score,
                                                            score.round.r_type) if classification is not None else None

        categories.append(category)

    bow_types = BowTypes.query.order_by(db.desc(BowTypes.name)).all()

    return render_template('site/archer.html', archer=archer, categories=categories, bow_types=bow_types)


def get_key(item):
    if isinstance(item, Archers):
        return item.first_name + ' ' + item.last_name
    else:
        return item.name


def is_integer(value):
    try:
        int(value)
        return True
    except Exception:
        return False


def is_category(value):
    return u'N' in value or u'E' in value[0:]


def is_date(value):
    try:
        date.fromtimestamp(mktime(strptime(value, '%Y-%m-%d')))
        return True
    except Exception:
        return False


def category_map(value):
    if 'N' in value:
        return u'Novice'
    else:
        return u'Experienced'
