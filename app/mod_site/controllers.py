import json

from flask import Blueprint, render_template, request, Response, redirect
from app.models import IndividualRecords, BowTypes, db, Archers, Scores, Classifications, Rounds, Events

mod_site = Blueprint('site', __name__)


@mod_site.route('/', methods=['GET'])
def home():
    indoor_indiv_scores = IndividualRecords.query.filter(
        db.or_(IndividualRecords.round_type == 'Indoors', IndividualRecords.round_type == 'WA Indoors')).order_by(
        IndividualRecords.round_name, db.desc(IndividualRecords.category), db.desc(IndividualRecords.bow_type),
        IndividualRecords.gender, db.desc(IndividualRecords.score)).all()

    outdoor_indiv_scores = IndividualRecords.query.filter(db.not_(
        db.or_(IndividualRecords.round_type == 'Indoors', IndividualRecords.round_type == 'WA Indoors'))).order_by(
        IndividualRecords.round_name, db.desc(IndividualRecords.category), db.desc(IndividualRecords.bow_type),
        IndividualRecords.gender, db.desc(IndividualRecords.score)).all()

    bow_types = BowTypes.query.order_by(db.desc(BowTypes.name)).all()

    return render_template('site/search.html', indoor_indiv_scores=indoor_indiv_scores,
                           outdoor_indiv_scores=outdoor_indiv_scores, bow_types=bow_types)


@mod_site.route('/search', methods=['POST'])
def search():
    if request.form['search_data']:
        data = json.loads(request.form['search_data'])
        if not data['data']:
            return Response(400)
        else:
            s_type = data['data']['s_type']
            s_id = data['data']['id']
            if not s_type or not s_id:
                return Response(400)
            else:
                return redirect('/records/{}/{}'.format(s_type, s_id))
    else:
        return 'Hello, world'
        # TODO: Resolve query, if ambiguous take user to disambiguation page


@mod_site.route('/event/<int:event_id>')
def event_by_id(event_id):
    if not db.session.query(db.exists().where(Events.id == event_id)).scalar():
        # TODO: State round not found or something.
        return redirect('/records/404')

    event = Events.query.get(event_id)
    categories_shot = db.session.query(Scores.date.distinct().label('date')).filter(
        Scores.event_id == event_id).order_by(db.desc(Scores.date)).all()
    categories = []
    for cat in categories_shot:
        category = {
            'date': cat.date
        }
        categories.append(category)
    return render_template('site/event.html', event=event, categories=categories)


@mod_site.route('/round/<int:round_id>')
def round_by_id(round_id):
    if not db.session.query(db.exists().where(Rounds.id == round_id)).scalar():
        # TODO: State round not found or something.
        return redirect('/records/404')

    round = Rounds.query.get(round_id)
    categories_shot = db.session.query(Scores.bow_type.distinct().label('bow_type'), Archers.gender.label('gender'),
                                       (Archers.gender + ' ' + BowTypes.name).label('div_name')).filter(
        Scores.round_id == round_id).join(Scores.archer).join(Scores.bow).order_by(Scores.bow_type).order_by(
        Archers.gender).all()
    categories = []
    for cat in categories_shot:
        category = {
            'bow_type': cat.bow_type,
            'div_name': cat.div_name,
            'scores': Scores.query.filter(Scores.round_id == round_id).filter(Scores.bow_type == cat.bow_type).filter(
                Archers.gender == cat.gender).join(Scores.archer).order_by(db.desc(Scores.score)).order_by(
                db.desc(Scores.num_hits)).order_by(db.desc(Scores.num_golds)).order_by(db.desc(Scores.num_xs)).all(),
            'max_score': round.max_score
        }

        for score in category['scores']:
            classification = Classifications.query.get((score.round_id, score.bow_type, cat.gender))
            score.classification = classification.get_class(score.score,
                                                            score.round.r_type) if classification is not None else None

        categories.append(category)
    return render_template('site/round.html', round=round, categories=categories)


@mod_site.route('/archer/<int:archer_id>')
def archer_by_id(archer_id):
    if not db.session.query(db.exists().where(Archers.id == archer_id)).scalar():
        # TODO: State archer not found or something.
        return redirect('/records/404')

    archer = Archers.query.get(archer_id)
    categories_shot = db.session.query(Scores.round_id.distinct().label('round_id'), Scores.bow_type.label('bow_type'),
                                       (Rounds.name + ' ' + BowTypes.name).label('div_name')).filter(
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
    return render_template('site/archer.html', archer=archer, categories=categories)
