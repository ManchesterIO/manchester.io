from flask import jsonify
from shapely.geometry import Point


class SearchResults(object):

    def __init__(self, app, statsd, location_service):
        self._app = app
        self._statsd = statsd
        self._location_service = location_service

    def init(self):
        self._app.add_url_rule('/search/rail-stations/near/<float:lat>,<float:lon>', 'rail-search', self.render)

    def render(self, lat, lon):
        self._statsd.incr(__name__ + '.requests')
        results = self._location_service.search_nearby(Point(lon, lat), 'rail-station', radius=5000)
        if results.count() < 5:
            results = self._location_service.search_nearby(Point(lon, lat), 'rail-station')[:5]
        return jsonify({'results': map(self._render_result, results)})

    def _render_result(self, result):
        return {
            'name': result['name'],
            'stop-type': result['stop-type'],
            'location': result['location']
        }
