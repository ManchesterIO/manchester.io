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
        self._app.add_url_rule('/rail-stations/<crs>',
                               'rail-station',
                               self.render,
                               defaults={'station_type': 'rail-station'})
        self._app.add_url_rule('/metrolink-stations/<crs>',
                               'metrolink-station',
                               self.render,
                               defaults={'station_type': 'metrolink-station'})

    def render(self, station_type, crs):
        self._statsd.incr(__name__ + '.requests')
        station = self._location_service.find(station_type, crs)
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
        routes_by_destination = defaultdict(list)
        for service in services:
            service['route'] = self._get_route(service, routes_from)
            routes_by_destination[self._get_destination(service)].append(service)
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
        for destination, services in routes_by_destination.items():
            sub_routes = list({service['route'] for service in services})
            friendly_destination = self._get_friendly_station(destination)
            routes[friendly_destination] = services
            if len(sub_routes) > 1:
                vias = self._make_friendly_vias(sub_routes)
                for service in services:
                    service['route_identifier'] = vias[service['route']]
            else:
                for service in services:
                    service['route_identifier'] = ''
        return routes

    def _get_friendly_station(self, tiploc):
        return self._location_service.fetch_name(tiploc=tiploc, default=tiploc)

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
                friendly_via = 'via {}'.format(self._get_friendly_station(distinct_stop))
            vias[stations] = friendly_via
        return vias

    def _transform_services(self, services, at):
        for destination in services:
            services[destination] = map(lambda service: self._make_departures(service, at), services[destination])

    def _make_departures(self, service, at):
        for calling_point in service['calling_points']:
            if calling_point['tiploc'] in at:
                break
        return {
            'service_id': calling_point['activation_id'],
            'service_type': calling_point['service_type'],
            'public_departure': calling_point['public_departure'],
            'predicted_departure': calling_point['predicted_departure'],
            'state': calling_point['state'],
            'platform': calling_point['predicted_platform'],
            'route': map(self._get_friendly_station, service['route']),
            'route_identifier': service['route_identifier']
        }
