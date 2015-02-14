from collections import defaultdict
from datetime import timedelta, datetime
from itertools import chain
import logging
from flask import abort, jsonify

LOGGER = logging.getLogger(__name__)


class Stations(object):

    def __init__(self, app, statsd, location_service, schedule_service):
        self._app = app
        self._statsd = statsd
        self._location_service = location_service
        self._schedule_service = schedule_service

    def init(self):
        self._app.add_url_rule('/rail-stations/<crs>', 'rail-station', self.render)

    def render(self, crs):
        self._statsd.incr(__name__ + '.requests')
        station = self._location_service.find('rail-station', crs)
        if station is None:
            abort(404)

        return jsonify({
            'name': station['name'],
            'stop-type': station['stop-type'],
            'location': station['location'],
            'departures': self._fetch_departures(tiploc=station['tiploc'])
        })

    def _fetch_departures(self, tiploc):
        services = []
        for service in self._schedule_service.upcoming_departures(end_time=datetime.now() + timedelta(minutes=90),
                                                                  tiploc=tiploc):
            services.append(service)
        routes_by_destination = self._group_by_route(services, routes_from=tiploc)
        friendly_routes = self._make_routes_friendly(routes_by_destination)
        self._transform_services(friendly_routes, tiploc)
        return friendly_routes

    def _group_by_route(self, services, routes_from):
        routes_by_destination = defaultdict(lambda: defaultdict(list))
        for service in services:
            routes_by_destination[self._get_destination(service)][self._get_route(service, routes_from)].append(service)
        return routes_by_destination

    def _get_destination(self, service):
        return service['calling_points'][-1]['tiploc']

    def _get_route(self, service, routes_from):
        calling_points = self._get_public_calling_points(service['calling_points'])
        i = 0
        for tiploc in routes_from:
            if tiploc in calling_points:
                i = calling_points.index(tiploc)
        return tuple(calling_points[i:])

    def _get_public_calling_points(self, calling_points):
        ids = []
        for calling_point in calling_points:
            if calling_point['public_arrival'] is not None or calling_point['public_departure'] is not None:
                ids.append(calling_point['tiploc'])
        return ids

    def _make_routes_friendly(self, routes_by_destination):
        routes = {}
        for destination, sub_routes in routes_by_destination.items():
            friendly_destination = self._location_service.fetch_name(tiploc=destination, default=destination)
            routes[friendly_destination] = {}
            if len(sub_routes) == 1:
                routes[friendly_destination][''] = sub_routes.popitem()[1]
            else:
                vias = self._make_friendly_vias(sub_routes.keys())
                for sub_route, services in sub_routes.items():
                    routes[friendly_destination][vias[sub_route]] = services
        return routes

    def _make_friendly_vias(self, sub_routes):
        vias = {}
        for i, stations in enumerate(sub_routes):
            all_stops = set(chain(*sub_routes))
            other_stops = set(chain(chain(*sub_routes[:i]), chain(*sub_routes[i+1:])))
            this_stops = set(stations)
            distinct_stops = other_stops - this_stops
            if len(distinct_stops) == 0:
                friendly_via = 'Fast Service'
            elif this_stops == all_stops:
                friendly_via = 'Stopping Service'
            else:
                distinct_stop = distinct_stops.pop()
                friendly_via = 'via {}'.format(
                    self._location_service.fetch_name(tiploc=distinct_stop, default=distinct_stop))
            vias[stations] = friendly_via
        return vias

    def _transform_services(self, services, at):
        for destination in services:
            for route in services[destination]:
                services[destination][route] = map(lambda service: self._make_departures(service, at),
                                                   services[destination][route])

    def _make_departures(self, service, at):
        for calling_point in service['calling_points']:
            if calling_point['tiploc'] in at:
                break
        return {
            'service_id': calling_point['activation_id'],
            'public_departure': calling_point['public_departure'],
            'predicted_departure': calling_point['predicted_departure'],
            'state': calling_point['state'],
            'platform': calling_point['predicted_platform']
        }
