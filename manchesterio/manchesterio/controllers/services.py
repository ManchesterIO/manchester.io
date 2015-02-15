from collections import OrderedDict
from datetime import datetime
from flask import abort, render_template
import requests
from requests.exceptions import HTTPError


class ServiceDisplay(object):

    def __init__(self, app, statsd):
        self._app = app
        self._statsd = statsd

    def init(self):
        self._app.add_url_rule('/trains/<service_id>', 'train', self.render)

    def render(self, service_id):
        self._statsd.incr(__name__ + 'render')
        try:
            service = self._fetch_results(service_id)
        except HTTPError as http_error:
            abort(http_error.response.status_code)

        return render_template('service.html',
                               service=self._transform_service(service))

    def _fetch_results(self, service_id):
        url = 'http://{base_url}/trains/{service_id}'.format(
            base_url=self._app.config['API_BASE_URL'],
            service_id=service_id
        )
        with self._statsd.timer(__name__ + '.request_time'):
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()

    def _transform_service(self, service):
        calling_points = map(self._transform_calling_point, service['calling_points'])
        return {
            'name': '{departure_time} {origin} to {destination}'.format(
                departure_time=calling_points[0]['public_departure'].strftime('%H:%M'),
                origin=calling_points[0]['station'],
                destination=calling_points[-1]['station']
            ),
            'calling_points': calling_points
        }

    def _transform_calling_point(self, calling_point):
        if calling_point['station']:
            station_name = calling_point['station']['name']
            station_url = '/rail-stations/{}'.format(calling_point['station']['identifier'])
        else:
            station_name = calling_point['tiploc']
            station_url = None

        return {
            'station': station_name,
            'station_url': station_url,
            'public_arrival': self._transform_to_time(calling_point['public_arrival']),
            'predicted_arrival': self._transform_to_time(calling_point['predicted_arrival']),
            'actual_arrival': self._transform_to_time(calling_point['actual_arrival']),
            'predicted_departure': self._transform_to_time(calling_point['predicted_departure']),
            'public_departure': self._transform_to_time(calling_point['public_departure']),
            'actual_departure': self._transform_to_time(calling_point['actual_departure']),
            'state': calling_point['state'],
            'platform': calling_point['predicted_platform']
        }

    def _transform_to_time(self, timestamp):
        if timestamp:
            return datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %Z')
        else:
            return None