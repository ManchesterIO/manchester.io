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
        self._app.add_url_rule('/rail-stations/<preferred_identifier>',
                               'rail-station',
                               self.render,
                               defaults={'station_type': 'rail-station', 'timetable_identifier_namespace': 'tiploc'})
        self._app.add_url_rule('/metrolink-stations/<preferred_identifier>',
                               'metrolink-station',
                               self.render,
                               defaults={'station_type': 'metrolink-station', 'timetable_identifier_namespace': 'atco'})

    def render(self, station_type, preferred_identifier, timetable_identifier_namespace):
        self._statsd.incr(__name__ + '.requests')
        station = self._location_service.find(station_type, preferred_identifier)
        if station is None:
            abort(404)

        return jsonify({
            'name': station['name'],
            'stop-type': station['stop-type'],
            'location': station['location'],
            'departures': self._fetch_departures(timetable_identifier_namespace, station[timetable_identifier_namespace])
        })

    def _fetch_departures(self, namespace, identifier):
        services = []
        for service in self._schedule_service.upcoming_departures(end_time=datetime.now() + timedelta(minutes=90),
                                                                  **{namespace: identifier}):
            services.append(service)
        routes_by_destination = self._group_by_route(services, namespace, routes_from=identifier)
        friendly_routes = self._make_routes_friendly(routes_by_destination, namespace)
        self._transform_services(friendly_routes, namespace, identifier)
        return friendly_routes

    def _group_by_route(self, services, namespace, routes_from):
        routes_by_destination = defaultdict(list)
        for service in services:
            service['route'] = self._get_route(service, namespace, routes_from)
            routes_by_destination[self._get_destination(service, namespace)].append(service)
        return routes_by_destination

    def _get_destination(self, service, namespace):
        return service['calling_points'][-1][namespace]

    def _get_route(self, service, namespace, routes_from):
        calling_points = self._get_public_calling_points(namespace, service['calling_points'])
        i = 0
        for identifier in routes_from:
            if identifier in calling_points:
                i = calling_points.index(identifier)
        return tuple(calling_points[i:])

    def _get_public_calling_points(self, namespace, calling_points):
        ids = []
        for calling_point in calling_points:
            if calling_point['public_arrival'] is not None or calling_point['public_departure'] is not None:
                ids.append(calling_point[namespace])
        return ids

    def _make_routes_friendly(self, routes_by_destination, namespace):
        routes = {}
        for destination, services in routes_by_destination.items():
            sub_routes = list({service['route'] for service in services})
            friendly_destination = self._get_friendly_station(namespace, destination)
            routes[friendly_destination] = services
            if len(sub_routes) > 1:
                vias = self._make_friendly_vias(sub_routes, namespace)
                for service in services:
                    service['route_identifier'] = vias[service['route']]
            else:
                for service in services:
                    service['route_identifier'] = ''
        return routes

    def _get_friendly_station(self, namespace, identifier):
        return self._location_service.fetch_name(**{namespace: identifier, 'default': identifier})

    def _make_friendly_vias(self, sub_routes, namespace):
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
                friendly_via = 'via {}'.format(self._get_friendly_station(namespace, distinct_stop))
            vias[stations] = friendly_via
        return vias

    def _transform_services(self, services, namespace, at):
        for destination in services:
            services[destination] = map(lambda service: self._make_departures(service, namespace, at),
                                        services[destination])[:5]

    def _make_departures(self, service, namespace, at):
        for calling_point in service['calling_points']:
            if calling_point[namespace] in at:
                break
        return {
            'service_id': calling_point['activation_id'],
            'service_type': calling_point['service_type'],
            'public_departure': calling_point['public_departure'],
            'predicted_departure': calling_point['predicted_departure'],
            'state': calling_point['state'],
            'platform': calling_point['predicted_platform'],
            'route': map(lambda station_id: self._get_friendly_station(namespace, station_id), service['route']),
            'route_identifier': service['route_identifier']
        }
