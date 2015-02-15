from collections import OrderedDict
from datetime import datetime
from flask import abort, render_template
import requests
from requests.exceptions import HTTPError


class StationDisplay(object):

    def __init__(self, app, statsd):
        self._app = app
        self._statsd = statsd

    def init(self):
        self._app.add_url_rule('/rail-stations/<crs>', 'rail-station', self.render)

    def render(self, crs):
        self._statsd.incr(__name__ + 'render')
        try:
            station = self._fetch_results(crs)
        except HTTPError as http_error:
            abort(http_error.response.status_code)

        return render_template('station.html',
                               station=station,
                               departures=self._transform_departures(station['departures']))

    def _fetch_results(self, crs):
        url = 'http://{base_url}/rail-stations/{crs}'.format(
            base_url=self._app.config['API_BASE_URL'],
            crs=crs
        )
        with self._statsd.timer(__name__ + '.request_time'):
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()

    def _transform_departures(self, departures):
        sorted_departures = OrderedDict()
        for destination in sorted(departures):
            sorted_departures[destination] = sorted(
                map(self._transform_service, departures[destination]),
                key=lambda service: service['public_departure']
            )
        return sorted_departures

    def _transform_service(self, service):
        return {
            'url': '/trains/{}'.format(service['service_id']),
            'public_departure': datetime.strptime(service['public_departure'], '%a, %d %b %Y %H:%M:%S %Z'),
            'predicted_departure': datetime.strptime(service['predicted_departure'], '%a, %d %b %Y %H:%M:%S %Z'),
            'state': service['state'],
            'platform': service['platform'],
            'route': service['route'],
            'route_identifier': service['route_identifier']
        }
