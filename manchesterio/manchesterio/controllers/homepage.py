from flask import render_template


class Homepage(object):

    def __init__(self, app, statsd):
        self._app = app
        self._statsd = statsd

    def init(self):
        self._app.add_url_rule('/', 'homepage', self.render_home)
        self._app.add_url_rule('/about', 'about', self.render_about)

    def render_home(self):
        self._statsd.incr(__name__ + '.render_home')
        return render_template('homepage.html')

    def render_about(self):
        self._statsd.incr(__name__ + '.render_about')
        return render_template('about.html')
