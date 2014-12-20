import os

from flask import Flask

from manchesterio.controllers.homepage import homepage

app = Flask(__name__)
app.debug = os.environ.get('DEBUG', 'false') == 'true'

app.add_url_rule('/', 'homepage', homepage)
