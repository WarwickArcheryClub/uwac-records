import json
from datetime import date

from flask import Blueprint, request, Response, abort
from app import db
from app.models import Rounds, Events, Archers, Scores
from app.mod_site.controllers import condense_category
import Levenshtein as Lev

mod_api = Blueprint('api', __name__, url_prefix='/api')


@mod_api.route('/suggestions', methods=['POST'])
def all_suggestions():
    if not request.form['query']:
        abort(400)

    query = request.form['query']

    suggestions = map(SuggestionUtils.to_suggestion,
                      Rounds.query.filter(Rounds.name.ilike(u'%{}%'.format(query))).all())
    suggestions.extend(map(SuggestionUtils.to_suggestion,
                           Events.query.filter(Events.name.ilike(u'%{}%'.format(query))).all()))
    suggestions.extend(map(SuggestionUtils.to_suggestion,
                           Archers.query.filter(
                               (Archers.first_name + u' ' + Archers.last_name).ilike(u'%{}%'.format(query))).all()))

    response = Response(
        json.dumps({'suggestions': sorted(suggestions, key=SuggestionUtils.get_key,
                                          cmp=lambda x, y: Lev.distance(x, query) - Lev.distance(y, query))}))
    response.headers['Content-Type'] = 'application/json'
    return response


@mod_api.route('/suggestions/archers', methods=['POST'])
def archers_suggestions():
    if not request.form['query']:
        abort(400)

    query = request.form['query']

    suggestions = map(SuggestionUtils.to_select2, Archers.query.filter(
        (Archers.first_name + " " + Archers.last_name).ilike(u'%{}%'.format(query))).all())

    response = Response(json.dumps({'results': sorted(suggestions, key=SuggestionUtils.get_select2_key,
                                                      cmp=lambda x, y: Lev.distance(x, query) - Lev.distance(y,
                                                                                                             query))}))
    response.headers['Content-Type'] = 'application/json'
    return response


@mod_api.route('/suggestions/rounds', methods=['POST'])
def rounds_suggestions():
    if not request.form['query']:
        abort(400)

    query = request.form['query']

    suggestions = map(SuggestionUtils.to_select2, Rounds.query.filter(Rounds.name.ilike(u'%{}%'.format(query))).all())

    response = Response(json.dumps({'results': sorted(suggestions, key=SuggestionUtils.get_select2_key,
                                                      cmp=lambda x, y: Lev.distance(x, query) - Lev.distance(y,
                                                                                                             query))}))
    response.headers['Content-Type'] = 'application/json'
    return response


@mod_api.route('/suggestions/events', methods=['POST'])
def events_suggestions():
    if not request.form['query']:
        abort(400)

    query = request.form['query']

    suggestions = map(SuggestionUtils.to_select2, Events.query.filter(Events.name.ilike(u'%{}%'.format(query))).all())

    response = Response(json.dumps({'results': sorted(suggestions, key=SuggestionUtils.get_select2_key,
                                                      cmp=lambda x, y: Lev.distance(x, query) - Lev.distance(y,
                                                                                                             query))}))
    response.headers["Content-Type"] = 'application/json'
    return response


@mod_api.route('/scores/from/<date:start_date>/to/<date:end_date>', methods=['GET'])
def export_scores_csv(start_date, end_date):
    scores = Scores.query.filter(Scores.date.between(start_date, end_date)).order_by(db.asc(Scores.date)).all()

    response = Response('{csv_head}\n{csv_body}'.format(csv_head=csv_head(),
                                                        csv_body=''.join(map(score_to_csv, scores))))

    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'inline; filename=scores-{start}-to-{end}.csv'.format(start=start_date,
                                                                                                    end=end_date)

    return response


def csv_head():
    return 'Name,Category,Bow Type,Round,Date,Event,Score,Hits,Gold,Xs,'


def score_to_csv(score):
    return '{name_csv},{cat_csv},{bow_csv},{round_csv},{date_csv},{event_csv},{score_csv},{hits_csv},' \
           '{golds_csv},{xs_csv},\n'.format(name_csv=score.archer.get_name(),
                                            cat_csv=condense_category(score.archer.gender, score.category),
                                            bow_csv=score.bow.name,
                                            round_csv=score.round.name, date_csv=date.strftime(score.date, '%d/%m/%Y'),
                                            event_csv=score.event.name,
                                            score_csv=score.score, hits_csv=score.num_hits, golds_csv=score.num_golds,
                                            xs_csv=score.num_xs or '')


class SuggestionUtils:
    def __init__(self):
        pass

    @staticmethod
    def get_key(item):
        return item['value']

    @staticmethod
    def get_select2_key(item):
        return item['text']

    @staticmethod
    def to_suggestion(item):
        if type(item) is Rounds:
            return {'data': {'id': item.id, 's_type': 'round'}, 'value': item.name}
        elif type(item) is Events:
            return {'data': {'id': item.id, 's_type': 'event'}, 'value': item.name}
        elif type(item) is Archers:
            return {'data': {'id': item.id, 's_type': 'archer'}, 'value': item.get_name()}
        else:
            return None

    @staticmethod
    def to_select2(item):
        if type(item) is Rounds:
            return {'id': item.id, 'text': item.name, 'max_hits': item.max_hits, 'max_score': item.max_score,
                    'type': item.r_type}
        else:
            return {'id': item.id, 'text': item.get_name() if type(item) is Archers else item.name}

    @staticmethod
    def to_complex_suggestion(item):
        if type(item) is Rounds:
            return {'value': item.name, 'data': {'id': item.id, 'type': item.r_type, 'max_hits': item.max_hits,
                                                 'max_score': item.max_score}}
        elif type(item) is Events:
            return {'data': {'id': item.id, 's_type': 'event'}, 'value': item.name}
        elif type(item) is Archers:
            return {'data': {'id': item.id, 's_type': 'archer'}, 'value': item.get_name()}
        else:
            return None
