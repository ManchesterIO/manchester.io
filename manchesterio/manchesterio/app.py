import os

from flask import Flask

from manchesterio.controllers.homepage import homepage
from manchesterio.controllers.search import search_results
from manchesterio.helpers.float_converter import NegativeFloatConverter

app = Flask(__name__)
app.debug = os.environ.get('DEBUG', 'false') == 'true'

app.url_map.converters['float'] = NegativeFloatConverter

app.add_url_rule('/', 'homepage', homepage)
app.add_url_rule('/search/rail-stations/near/<float:lat>,<float:lon>', 'rail-search', search_results)
