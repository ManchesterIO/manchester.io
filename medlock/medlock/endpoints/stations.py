from flask import abort, jsonify


class Stations(object):

    def __init__(self, app, statsd, location_service, schedule_service):
        self._app = app
        self._statsd = statsd
        self._location_service = location_service
        self._schedule_service = schedule_service

    def init(self):
        self._app.add_url_rule('/rail-station/<crs>', 'rail-station', self.render)

    def render(self, crs):
        self._statsd.incr(__name__ + '.requests')
        station = self._location_service.find('rail-station', crs)
        if station is None:
            abort(404)

        return jsonify({
            'name': station['name'],
            'stop-type': station['stop-type'],
            'location': station['location'],
            'services': list(self._fetch_services(tiploc=station['tiploc']))
        })

    def _fetch_services(self, tiploc):
        services = []
        for service in self._schedule_service.activations_at(tiploc=tiploc):
            del service['_id']
            services.append(service)
        return services
