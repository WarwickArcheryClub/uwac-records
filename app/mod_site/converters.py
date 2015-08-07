from time import strptime, mktime
from datetime import date

from werkzeug.routing import BaseConverter


class DateConverter(BaseConverter):

    def to_python(self, value):
        return date.fromtimestamp(mktime(strptime(value, '%Y-%m-%d')))

    def to_url(self, value):
        return value.strftime('%Y-%m-%d')
