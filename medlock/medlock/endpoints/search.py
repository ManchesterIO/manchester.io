from flask import abort, jsonify
from shapely.geometry import Point


class SearchResults(object):

    _STATION_TYPES = {
        'rail-stations': ('rail-station', 5000),
        'metrolink-stations': ('metrolink-station', 750),
        'bus-stops': ('bus-stop', 350)
    }

    def __init__(self, app, statsd, location_service):
        self._app = app
        self._statsd = statsd
        self._location_service = location_service

    def init(self):
        self._app.add_url_rule('/search/<station_type>/near/<float:lat>,<float:lon>', 'rail-search', self.render)

    def render(self, station_type, lat, lon):
        if station_type not in self._STATION_TYPES:
            abort(404)

        station_type, radius = self._STATION_TYPES[station_type]

        self._statsd.incr(__name__ + '.requests')
        results = self._location_service.search_nearby(Point(lon, lat),station_type, radius=radius)
        if results.count() < 5:
            results = self._location_service.search_nearby(Point(lon, lat), station_type)[:5]
        return jsonify({'results': map(self._render_result, results)})

    def _render_result(self, result):
        return {
            'name': result['name'],
            'stop-type': result['stop-type'],
            'location': result['location'],
            'identifier': result['identifier']
        }
