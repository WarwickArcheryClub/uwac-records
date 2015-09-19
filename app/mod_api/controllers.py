import json

from flask import Blueprint, request, Response, abort
from app.models import Rounds, Events, Archers
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
