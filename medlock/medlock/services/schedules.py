from datetime import timedelta, datetime, time
import logging

from bson.tz_util import utc
from pymongo import ASCENDING

LOGGER = logging.getLogger(__name__)


class ScheduleService(object):

    EN_ROUTE_EVENT = 'en-route'
    ARRIVAL_EVENT = 'arrival'
    DEPARTURE_EVENT = 'departure'
    CANCELLED_EVENT = 'cancelled'

    def __init__(self, statsd, mongo):
        self._statsd = statsd
        self._kv_store = mongo
        self._kv_schedule_collection = None
        self._kv_association_collection = None
        self._kv_activations_collection = None

    def insert(self, **kwargs):
        self._statsd.incr(__name__ + '.insert')
        self._schedule_collection.insert(kwargs)

    def delete(self, **kwargs):
        self._statsd.incr(__name__ + '.delete')
        self._schedule_collection.remove(kwargs)

    def create_association(self, **kwargs):
        self._statsd.incr(__name__ + '.create_association')
        self._association_collection.insert(kwargs)

    def delete_association(self, **kwargs):
        self._statsd.incr(__name__ + '.delete_association')
        self._association_collection.remove(kwargs)

    def reset(self, source):
        self._association_collection.remove({'source': source})
        self._schedule_collection.remove({'source': source})

    def remove_expired(self, today, source):
        self._association_collection.remove({'source': source, 'association_end': {'$lt': today.isoformat()}})
        self._schedule_collection.remove({'source': source, 'service_end': {'$lt': today.isoformat()}})
        self._activations_collection.remove(
            {'activated_on': {'$lt': datetime.combine(today - timedelta(days=1), time.min)}}
        )

    def upcoming_departures(self, end_time, **identifiers):
        departures = []
        self._statsd.incr(__name__ + '.activations_search')

        query = {
            '$or': [
                {'public_departure': {'$lt': end_time}},
                {'predicted_departure': {'$lt': end_time}}
            ],
            'state': {'$in': [self.EN_ROUTE_EVENT, self.ARRIVAL_EVENT, self.CANCELLED_EVENT]}
        }
        for identifier, values in identifiers.items():
            query[identifier] = {'$in': values}

        for departure in self._activations_collection.find(query):
            departures.append({
                'calling_points': sorted(self._activations_collection.find({
                    'activation_id': departure['activation_id'],
                    'service_type': departure['service_type']
                }), key=lambda activation: activation['arrival'] or datetime.min.replace(tzinfo=utc))
            })

        return departures

    def activate_schedule(self, activation_id, service_type, activation_date, service_id, schedule_start):
        self._statsd.incr(__name__ + '.activate_schedule')
        schedule = self._get_schedule_to_activate(service_id, schedule_start)
        if schedule:
            self._create_activation(activation_id, service_type, activation_date, schedule)
            self._statsd.incr(__name__ + '.activate_schedule_success')
            return True
        else:
            self._statsd.incr(__name__ + '.activate_schedule_no_schedule')
            return False

    def update_activation(self, activation_id, service_type, calling_point_planned_timestamp, event, actual_timestamp):
        if event == self.ARRIVAL_EVENT:
            self._statsd.incr(__name__ + '.movements.arrival')
            query_field = 'arrival'
            update_field = 'actual_arrival'
        elif event == self.DEPARTURE_EVENT:
            self._statsd.incr(__name__ + '.movements.departure')
            query_field = 'departure'
            update_field = 'actual_departure'
        else:
            self._statsd.incr(__name__ + '.movements.invalid')
            LOGGER.error("Attempted to update activation %s with invalid event %s", activation_id, event)
            return False

        result = self._activations_collection.update(
            {
                'activation_id': activation_id,
                'service_type': service_type,
                query_field: calling_point_planned_timestamp
            },
            {'$set': {update_field: actual_timestamp}}
        )
        if not result['updatedExisting']:
            if self._activations_collection.find({'activation_id': activation_id}).count() > 0:
                self._statsd.incr(__name__ + '.movements.invalid')
                return False
            else:
                self._statsd.incr(__name__ + '.movements.no_activation')
                return None
        else:
            self._statsd.incr(__name__ + '.movements.success')
            self._update_missed_records(activation_id, service_type, calling_point_planned_timestamp)
            return True

    def cancel_activation(self, activation_id, service_type, cancelled_from):
        self._statsd.incr(__name__ + '.cancellations')
        self._activations_collection.update(
            {
                'activation_id': activation_id,
                'service_type': service_type,
                'departure': {'$gte': cancelled_from},
            },
            {'$set': {'state': self.DEPARTURE_EVENT}}
        )

    def _update_missed_records(self, activation_id, service_type, planned_timestamp):
        self._activations_collection.update(
            {
                'activation_id': activation_id,
                'service_type': service_type,
                '$or': [
                    {'arrival': {'$lt': planned_timestamp}},
                    {'departure': {'$lt': planned_timestamp}},
                ],
                'state': {'$in': [self.EN_ROUTE_EVENT, self.ARRIVAL_EVENT]}
            },
            {'$set': {'state': self.DEPARTURE_EVENT}}
        )

    def _get_schedule_to_activate(self, service_id, schedule_start):
        schedules = self._schedule_collection.find(
            {'service_id': service_id, 'schedule_start': schedule_start}
        ).sort('schedule_priority')
        if schedules.count() > 0 and not self._is_planned_cancellation(schedules[0]):
            return schedules[0]
        else:
            return None

    def _is_planned_cancellation(self, schedule):
        return schedule['schedule_priority'] == 'C'

    def _create_activation(self, activation_id, service_type, activation_time, schedule):
        activations = []
        metadata = {
            'activation_id': activation_id,
            'activated_on': activation_time,
            'service_type': service_type
        }
        public_activation_date = activation_time.date()
        planned_activation_date = activation_time.date()
        last_public_time = time.min
        last_planned_time = time.min

        for calling_point in schedule['calling_points']:
            public_activation_date, last_public_time = self._convert_to_datetime(
                public_activation_date, calling_point, last_public_time, 'public_arrival')
            public_activation_date, last_public_time = self._convert_to_datetime(
                public_activation_date, calling_point, last_public_time, 'public_departure')

            planned_activation_date, last_planned_time = self._convert_to_datetime(
                planned_activation_date, calling_point, last_planned_time, 'arrival')
            planned_activation_date, last_planned_time = self._convert_to_datetime(
                planned_activation_date, calling_point, last_planned_time, 'departure')

            calling_point.update({
                'predicted_arrival': calling_point['public_arrival'],
                'predicted_departure': calling_point['public_departure'],
                'actual_arrival': None,
                'actual_departure': None,
                'predicted_platform': calling_point['platform'],
                'state': self.EN_ROUTE_EVENT
            })
            calling_point.update(metadata)
            activations.append(calling_point)

        self._activations_collection.insert(activations)

    def _convert_to_datetime(self, activation_date, calling_point, last_time, event):
        if calling_point[event]:
            calling_point_time = time(int(calling_point[event][:2]),
                                      int(calling_point[event][2:4]),
                                      int(calling_point[event][4:6] or 0))
            if last_time > calling_point_time:
                activation_date += timedelta(days=1)
            last_time = calling_point_time
            calling_point[event] = datetime.combine(activation_date, calling_point_time)
        return activation_date, last_time

    @property
    def _schedule_collection(self):
        if self._kv_schedule_collection is None:
            self._kv_schedule_collection = self._kv_store.db.schedules
            self._kv_schedule_collection.ensure_index('source')
            self._kv_schedule_collection.ensure_index({'source': ASCENDING, 'service_end': ASCENDING}.items())
            self._kv_schedule_collection.ensure_index({'service_id': ASCENDING,
                                                       'schedule_priority': ASCENDING,
                                                       'schedule_start': ASCENDING,
                                                       'source': ASCENDING}.items(),
                                                      name='schedule_delete_lookup')
            self._kv_schedule_collection.ensure_index({'service_id': ASCENDING, 'schedule_start': ASCENDING}.items())
        return self._kv_schedule_collection

    @property
    def _association_collection(self):
        if self._kv_association_collection is None:
            self._kv_association_collection = self._kv_store.db.associations
            self._kv_association_collection.ensure_index('source')
            self._kv_association_collection.ensure_index({'source': ASCENDING, 'association_end': ASCENDING}.items())
            self._kv_association_collection.ensure_index({'service_id': ASCENDING,
                                                          'schedule_priority': ASCENDING,
                                                          'association_start': ASCENDING,
                                                          'source': ASCENDING,
                                                          'associated_service_id': ASCENDING,
                                                          'associated_location': ASCENDING}.items(),
                                                         name='association_delete_lookup')
        return self._kv_association_collection

    @property
    def _activations_collection(self):
        if self._kv_activations_collection is None:
            self._kv_activations_collection = self._kv_store.db.activations
            self._kv_activations_collection.ensure_index({'activation_id': ASCENDING,
                                                          'service_type': ASCENDING,
                                                          'arrival': ASCENDING}.items())
            self._kv_activations_collection.ensure_index({'activation_id': ASCENDING,
                                                          'service_type': ASCENDING,
                                                          'departure': ASCENDING}.items())
            self._kv_activations_collection.ensure_index({'public_departure': ASCENDING,
                                                          'tiploc': ASCENDING,
                                                          'state': ASCENDING}.items())
            self._kv_activations_collection.ensure_index({'predicted_departure': ASCENDING,
                                                          'tiploc': ASCENDING,
                                                          'state': ASCENDING}.items())
            self._kv_activations_collection.ensure_index({'activation_id': ASCENDING,
                                                          'service_type': ASCENDING,
                                                          'arrival': ASCENDING}.items())
            self._kv_activations_collection.ensure_index({'activation_id': ASCENDING,
                                                          'service_type': ASCENDING,
                                                          'arrival': ASCENDING,
                                                          'state': ASCENDING}.items())
            self._kv_activations_collection.ensure_index({'activation_id': ASCENDING,
                                                          'service_type': ASCENDING,
                                                          'departure': ASCENDING}.items())
            self._kv_activations_collection.ensure_index({'activation_id': ASCENDING,
                                                          'service_type': ASCENDING,
                                                          'departure': ASCENDING,
                                                          'state': ASCENDING}.items())
            self._kv_activations_collection.ensure_index('activated_on')
        return self._kv_activations_collection
