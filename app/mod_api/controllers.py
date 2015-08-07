import json

from flask import Blueprint, request, Response, abort
from app.models import Rounds, Events, Archers
import Levenshtein as lev

mod_api = Blueprint('api', __name__, url_prefix='/api')


@mod_api.route('/suggestions', methods=['POST'])
def all_suggestions():
    if not request.form['query']:
        abort(400)

    query = request.form['query']

    suggestions = map(SuggestionUtils.to_suggestion,
                      Rounds.query.filter(Rounds.name.ilike('%{}%'.format(query))).all())
    suggestions.extend(map(SuggestionUtils.to_suggestion,
                           Events.query.filter(Events.name.ilike('%{}%'.format(query))).all()))
    suggestions.extend(map(SuggestionUtils.to_suggestion,
                           Archers.query.filter(
                               (Archers.first_name + ' ' + Archers.last_name).ilike('%{}%'.format(query))).all()))

    response = Response(
        json.dumps({'suggestions':
                        sorted(suggestions, key=SuggestionUtils.get_key,
                               cmp=lambda x, y: lev.distance(x, query) - lev.distance(y, query))}))
    response.headers['Content-Type'] = 'application/json'
    return response


@mod_api.route('/suggestions/archers', methods=['POST'])
def archers_suggestions():
    if not request.form['query']:
        abort(400)

    query = request.form['query']

    suggestions = map(SuggestionUtils.to_complex_suggestion,
                      Archers.query.filter(
                          (Archers.first_name + " " + Archers.last_name).ilike('%{}%'.format(query))).all())

    response = Response(json.dumps({'suggestions':
                                        sorted(suggestions, key=SuggestionUtils.get_key,
                                               cmp=lambda x, y: lev.distance(x, query) - lev.distance(y, query))}))
    response.headers['Content-Type'] = 'application/json'
    return response


@mod_api.route('/suggestions/rounds', methods=['POST'])
def rounds_suggestions():
    if not request.form['query']:
        abort(400)

    query = request.form['query']

    suggestions = map(SuggestionUtils.to_complex_suggestion,
                      Rounds.query.filter(Rounds.name.ilike('%{}%'.format(query))).all())

    response = Response(json.dumps({'suggestions':
                                        sorted(suggestions, key=SuggestionUtils.get_key,
                                               cmp=lambda x, y: lev.distance(x, query) - lev.distance(y, query))}))
    response.headers['Content-Type'] = 'application/json'
    return response


@mod_api.route('/suggestions/events', methods=['POST'])
def events_suggestions():
    if not request.form['query']:
        abort(400)

    query = request.form['query']

    suggestions = map(SuggestionUtils.to_complex_suggestion,
                      Events.query.filter(Events.name.ilike('%{}%'.format(query))).all())

    response = Response(json.dumps({'suggestions':
                                        sorted(suggestions, key=SuggestionUtils.get_key,
                                               cmp=lambda x, y: lev.distance(x, query) - lev.distance(y, query))}))
    response.headers["Content-Type"] = 'application/json'
    return response


class SuggestionUtils:
    def __init__(self):
        pass

    @staticmethod
    def get_key(item):
        return item['value']

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

    # TODO: Add other items for event and archers
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
