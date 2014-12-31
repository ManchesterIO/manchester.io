from flask import render_template


class Homepage(object):

    def __init__(self, app):
        self._app = app

    def init(self):
        self._app.add_url_rule('/', 'homepage', self.render_home)
        self._app.add_url_rule('/about', 'about', self.render_about)

    def render_home(self):
        return render_template('homepage.html')

    def render_about(self):
        return render_template('about.html')
