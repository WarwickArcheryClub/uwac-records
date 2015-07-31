import json

from flask import Blueprint, render_template, request, Response, redirect
from app.models import IndividualRecords, BowTypes, db, Archers, Scores, Classifications, Rounds

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

    return render_template('site/index.html', indoor_indiv_scores=indoor_indiv_scores,
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


@mod_site.route('/archer/<int:archer_id>')
def archer(archer_id):
    arch = Archers.query.get(archer_id)
    categories = db.session.query(Scores.round_id.distinct().label('round_id'), Scores.bow_type.label('bow_type'),
                                  (Rounds.name + ' ' + BowTypes.name).label('div_name')).filter(
        Scores.archer_id == archer_id).join(Scores.bow).join(Scores.round).all()
    scores = {}
    for cat in categories:
        scores[cat.div_name] = Scores.query.filter(Scores.archer_id == archer_id).filter(
            Scores.round_id == cat.round_id).filter(Scores.bow_type == cat.bow_type).all()
        for score in scores[cat.div_name]:
            classification = Classifications.query.get((score.round_id, score.bow_type, arch.gender))
            score.classification = classification.get_class(score.score,
                                                            score.round.r_type) if classification is not None else None
    # scores = Scores.query.filter(Scores.archer_id == archer_id).join(Scores.round).all()
    # for score in scores:
    #     classification = Classifications.query.get((score.round_id, score.bow_type, arch.gender))
    #     score.classification = classification.get_class(score.score,
    #                                                     score.round.r_type) if classification is not None else None
    if not archer:
        return Response(404)
    return render_template('site/archer.html', archer=arch, scores=scores)
