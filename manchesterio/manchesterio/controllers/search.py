from math import atan2, cos, degrees, sin

from flask import abort, render_template
from geopy.distance import distance as compute_distance
import requests


class SearchResults(object):

    _ACCEPTED_STATION_TYPES = {
        'rail-stations': 'rail stations',
        'metrolink-stations': 'Metrolink stations',
        'bus-stops': 'bus stops'
    }

    def __init__(self, app, statsd):
        self._app = app
        self._statsd = statsd

    def init(self):
        self._app.add_url_rule('/search/<station_type>/near/<float:lat>,<float:lon>', 'search', self.render)

    def render(self, station_type, lat, lon):
        if station_type not in self._ACCEPTED_STATION_TYPES:
            abort(404)

        self._statsd.incr(__name__ + 'render')
        stations = []
        for station in self._fetch_results(station_type, lat, lon).get('results', []):
            stations.append(self._station_to_template(station, station_type, (lat, lon)))
        if len(stations) == 0:
            self._statsd.incr(__name__ + 'no_results')
            abort(404)

        return render_template('search-results.html',
                               station_type=self._ACCEPTED_STATION_TYPES[station_type],
                               stations=stations,
                               starting_lat=lat, starting_lon=lon)

    def _fetch_results(self, station_type, lat, lon):
        url = 'http://{base_url}/search/{station_type}/near/{lat},{lon}'.format(
            base_url=self._app.config['API_BASE_URL'],
            station_type=station_type,
            lat=lat,
            lon=lon
        )
        with self._statsd.timer(__name__ + '.request_time'):
            return requests.get(url, timeout=5).json()

    def _station_to_template(self, station, station_type, origin):
        lat = station['location']['coordinates'][1]
        lon = station['location']['coordinates'][0]
        return {
            'name': station['name'],
            'stop_type': self._STOP_TYPES.get(station['stop-type'], ''),
            'lat': lat,
            'lon': lon,
            'url': '/{station_type}/{identifier}'.format(
                station_type=station_type, identifier=station['identifier']),
            'distance_and_bearing': '{distance} {bearing}'.format(
                distance=self._distance(origin, (lat, lon)),
                bearing=self._bearing(origin, (lat, lon))
            )
        }

    def _distance(self, origin, destination):
        distance = compute_distance(origin, destination)
        if distance.meters > 1000:
            return "{d}mi".format(d=round(distance.miles, 1))
        else:
            return "{d}m".format(d=int(distance.meters))

    def _bearing(self, (lat1, lon1), (lat2, lon2)):
        d_lon = lon2 - lon1
        y = sin(d_lon) * cos(lat2)
        x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(d_lon)
        bearing = degrees(atan2(y, x))
        if bearing < -157.5 or bearing >= 157.5:
            return 'S'
        elif -157.5 <= bearing < -112.5:
            return 'SE'
        elif -112.5 <= bearing < -67.5:
            return 'E'
        elif -67.5 <= bearing < -22.5:
            return 'NE'
        elif -22.5 <= bearing < 22.5:
            return 'N'
        elif 22.5 <= bearing < 67.5:
            return 'NW'
        elif 67.5 <= bearing < 112.5:
            return 'W'
        elif 112.5 <= bearing < 157.5:
            return 'SW'

    _STOP_TYPES = {
        'rail-station': 'Rail station',
        'metrolink-station': 'Metrolink station',
        'bus-stop': 'bus stop'
    }
