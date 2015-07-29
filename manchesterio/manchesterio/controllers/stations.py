from collections import OrderedDict
from datetime import datetime
from itertools import chain
from flask import abort, render_template
import requests
from requests.exceptions import HTTPError


class StationDisplay(object):

    def __init__(self, app, statsd):
        self._app = app
        self._statsd = statsd

    def init(self):
        self._app.add_url_rule(
            '/rail-stations/<identifier>', 'rail-station', self.render,
            defaults={'stop_type': 'rail-stations', 'service_type': 'trains'})
        self._app.add_url_rule(
            '/metrolink-stations/<identifier>', 'metrolink-station', self.render,
            defaults={'stop_type': 'metrolink-stations', 'service_type': 'trams'})

    def render(self, stop_type, identifier, service_type):
        self._statsd.incr(__name__ + 'render')
        try:
            station = self._fetch_results(stop_type, identifier)
        except HTTPError as http_error:
            abort(http_error.response.status_code)

        departures = self._transform_departures(station['departures'], service_type)

        return render_template('station.html',
                               station=station,
                               departures=departures,
                               has_platform_information=self._has_platform_information(departures))

    def _has_platform_information(self, departures):
        has_platform_information = False
        for service in chain(*departures.values()):
            if service['platform']:
                has_platform_information = True
        return has_platform_information

    def _fetch_results(self, stop_type, identifier):
        url = 'http://{base_url}/{stop_type}/{identifier}'.format(
            base_url=self._app.config['API_BASE_URL'],
            stop_type=stop_type,
            identifier=identifier
        )
        with self._statsd.timer(__name__ + '.request_time'):
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()

    def _transform_departures(self, departures, service_type):
        sorted_departures = OrderedDict()
        for destination in sorted(departures):
            sorted_departures[destination] = sorted(
                map(lambda service: self._transform_service(service, service_type), departures[destination]),
                key=lambda service: service['public_departure']
            )
        return sorted_departures

    def _transform_service(self, service, service_type):
        return {
            'url': '/{}/{}'.format(service_type, service['service_id']),
            'public_departure': datetime.strptime(service['public_departure'], '%a, %d %b %Y %H:%M:%S %Z'),
            'predicted_departure': datetime.strptime(service['predicted_departure'], '%a, %d %b %Y %H:%M:%S %Z'),
            'state': service['state'],
            'platform': service['platform'],
            'route': service['route'],
            'route_identifier': service['route_identifier']
        }
