from flask import Blueprint, render_template
from app.models import IndividualRecords, BowTypes, db

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
