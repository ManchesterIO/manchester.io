from flask import render_template


class Homepage(object):

    def __init__(self, app):
        self._app = app

    def init(self):
        self._app.add_url_rule('/', 'homepage', self.render)

    def render(self):
        return render_template('homepage.html')
