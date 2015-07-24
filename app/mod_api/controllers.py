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

    suggestions = map(_round_to_suggestion,
                      Rounds.query.filter(Rounds.name.ilike('%{}%'.format(query))).all())
    suggestions.extend(map(_event_to_suggestion,
                           Events.query.filter(Events.name.ilike('%{}%'.format(query))).all()))
    suggestions.extend(map(_archer_to_suggestion,
                           Archers.query.filter(
                               (Archers.first_name + " " + Archers.last_name).ilike('%{}%'.format(query))).all()))

    response = Response(
        json.dumps({'suggestions':
                        sorted(suggestions, key=_get_key,
                               cmp=lambda x, y: lev.distance(x, query) - lev.distance(y, query))}))
    response.headers["Content-Type"] = "application/json"
    return response


def _get_key(item):
    return item["value"]


def _round_to_suggestion(round):
    return {"data": {"id": round.id, "s_type": "round"}, "value": round.name}


def _event_to_suggestion(event):
    return {"data": {"id": event.id, "s_type": "event"}, "value": event.name}


def _archer_to_suggestion(archer):
    return {"data": {"id": archer.id, "s_type": "archer"}, "value": archer.get_name()}
