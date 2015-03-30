import logging
from flask import abort, jsonify

LOGGER = logging.getLogger(__name__)


class Services(object):

    def __init__(self, app, statsd, location_service, schedule_service):
        self._app = app
        self._statsd = statsd
        self._location_service = location_service
        self._schedule_service = schedule_service

    def init(self):
        self._app.add_url_rule(
            '/trains/<service_id>', 'train', self.render,
            defaults={'service_type': 'train', 'identifier_namespace': 'tiploc'})
        self._app.add_url_rule(
            '/trams/<service_id>', 'tram', self.render,
            defaults={'service_type': 'metrolink', 'identifier_namespace': 'atco'})

    def render(self, service_id, service_type, identifier_namespace):
        self._statsd.incr(__name__ + '.requests')
        service = self._schedule_service.fetch_activation(service_id, service_type)
        if not service.get('calling_points', []):
            abort(404)

        for calling_point in service['calling_points']:
            calling_point['station'] = self._location_service.find_by_additional_identifier(
                **{identifier_namespace: calling_point[identifier_namespace]}
            )
            if calling_point['station']:
                del calling_point['station']['_id']

        return jsonify(service)
