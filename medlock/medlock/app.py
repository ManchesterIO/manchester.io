from flask import Flask

import os

app = Flask(__name__)
app.debug = os.environ.get('DEBUG', 'false') == 'true'


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
