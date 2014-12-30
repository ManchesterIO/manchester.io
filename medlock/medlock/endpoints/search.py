from flask import jsonify


class SearchResults(object):

    def __init__(self, app):
        self._app = app

    def init(self):
        self._app.add_url_rule('/search/rail-stations/near/<float:lat>,<float:lon>', 'rail-search', self.render)

    def render(self, lat, lon):
        return jsonify([])
