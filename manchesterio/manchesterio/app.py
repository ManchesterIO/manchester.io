from flask import Flask
from flask.ext.statsd import StatsD
from raven.contrib.flask import Sentry

from manchesterio.controllers.homepage import Homepage
from manchesterio.controllers.search import SearchResults
from manchesterio.helpers.float_converter import NegativeFloatConverter

app = Flask('manchesterio')
app.config.from_envvar('CONFIG')

sentry = Sentry(app)

statsd = StatsD(app)

app.url_map.converters['float'] = NegativeFloatConverter

Homepage(app, statsd).init()
SearchResults(app, statsd).init()

if __name__ == '__main__':
    app.debug = True
    app.run(port=8000)
