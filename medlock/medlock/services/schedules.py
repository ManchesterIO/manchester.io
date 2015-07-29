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
    PREDICTED = 'predicted'
    ACTUAL = 'actual'

    def __init__(self, statsd, mongo):
        self._statsd = statsd
        self._kv_store = mongo
        self._kv_schedule_collection = None
        self._kv_activations_collection = None

    def insert(self, **kwargs):
        self._statsd.incr(__name__ + '.insert')
        self._schedule_collection.insert(kwargs)

    def delete(self, **kwargs):
        self._statsd.incr(__name__ + '.delete')
        self._schedule_collection.remove(kwargs)

    def reset(self, source):
        self._schedule_collection.remove({'source': source})

    def fetch_valid_schedules_for(self, day, service_type, bank_holiday, school_holiday):
        weekday = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][day.weekday()]
        query = {
            'schedule_start': {'$lt': day},
            'schedule_expires': {'$gt': day},
            'service_type': service_type,
            'activate_on.school-holidays': {'$in': [school_holiday, None]}
        }

        if bank_holiday:
            query['$or'] = [
                {'activate_on.{}'.format(weekday): True, 'activate_on.bank-holidays': {'$in': [True, None]}},
                {'activate_on.bank-holidays': 'always'}
            ]
        else:
            query['activate_on.{}'.format(weekday)] = True
            query['activate_on.bank-holidays'] = {'$in': [False, None]}

        return self._schedule_collection.find(query)

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

        for departure in self._activations_collection.find(
                query,
                projection={
                    '_id': False,
                    'activation_id': True,
                    'service_type': True
                }
        ):
            departures.append(self.fetch_activation(departure['activation_id'], departure['service_type']))

        return departures

    def fetch_activation(self, activation_id, service_type):
        calling_points = list(self._activations_collection.find({'activation_id': activation_id,
                                                                 'service_type': service_type}))
        for calling_point in calling_points:
            del calling_point['_id']
        return {'calling_points': sorted(calling_points, key=self._calling_point_sort_key)}

    def activate_schedule(self, activation_id, service_type, activation_date, service_id, schedule_start):
        self._statsd.incr(__name__ + '.activate_schedule')
        schedule = self._get_schedule_to_activate(service_id, schedule_start)
        if schedule:
            self._activations_collection.remove({'activation_id': activation_id})
            self._create_activation(activation_id, service_type, activation_date, schedule)
            self._statsd.incr(__name__ + '.activate_schedule_success')
            return True
        else:
            self._statsd.incr(__name__ + '.activate_schedule_no_schedule')
            return False

    def update_activation(
            self, activation_id, service_type, calling_point_planned_timestamp, event, actual_timestamp,
            actual_or_predicted
    ):
        if event == self.ARRIVAL_EVENT:
            self._statsd.incr(__name__ + '.movements.arrival')
            query_field = 'arrival'
        elif event == self.DEPARTURE_EVENT:
            self._statsd.incr(__name__ + '.movements.departure')
            query_field = 'departure'
        else:
            self._statsd.incr(__name__ + '.movements.invalid')
            LOGGER.error("Attempted to update activation %s with invalid event %s", activation_id, event)
            return False

        update = {
            "{0}_{1}".format(actual_or_predicted, query_field): actual_timestamp
        }

        if actual_or_predicted == 'actual':
            update['state'] = event

        result = self._activations_collection.update(
            {
                'activation_id': activation_id,
                'service_type': service_type,
                query_field: calling_point_planned_timestamp
            },
            {'$set': update}
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
            if actual_or_predicted == self.ACTUAL:
                self._update_missed_records(activation_id, service_type, calling_point_planned_timestamp)
            return True

    def bulk_manual_update(self, event_type, timestamp, service_type):
        self._activations_collection.update({'service_type': service_type, event_type: {'$lte': timestamp}},
                                            {'$set': {'state': event_type}},
                                            multi=True)

    def cancel_activation(self, activation_id, service_type, cancelled_from):
        result = self._activations_collection.update(
            {
                'activation_id': activation_id,
                'service_type': service_type,
                'departure': {'$gte': cancelled_from},
            },
            {'$set': {'state': self.CANCELLED_EVENT}},
            multi=True
        )
        if not result['updatedExisting']:
            if self._activations_collection.find({'activation_id': activation_id}).count() > 0:
                self._statsd.incr(__name__ + '.cancellations.invalid')
                return False
            else:
                self._statsd.incr(__name__ + '.cancellations.no_activation')
                return None
        else:
            self._statsd.incr(__name__ + '.cancellations.success')
            self._update_missed_records(activation_id, service_type, cancelled_from)
            return True

    def remove_activation(self, activation_id, service_type):
        self._activations_collection.remove({
            'activation_id': activation_id,
            'service_type': service_type
        })

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
            {'$set': {'state': self.DEPARTURE_EVENT}},
            multi=True
        )

    def _get_schedule_to_activate(self, service_id, schedule_start):
        schedule = self._schedule_collection.find_one(
            {'service_id': service_id, 'schedule_start': schedule_start}
        )
        return schedule

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

        if schedule['calling_points'] and int(schedule['calling_points'][0]['departure'][:2]) > 23:
            planned_activation_date += timedelta(days=1)
        if schedule['calling_points'] and int(schedule['calling_points'][0]['public_departure'][:2]) > 23:
            public_activation_date += timedelta(days=1)

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
            hour = int(calling_point[event][:2])
            if hour > 23:
                hour -= 24
            calling_point_time = time(hour,
                                      int(calling_point[event][2:4]),
                                      int(calling_point[event][4:6] or 0))
            if last_time > calling_point_time:
                activation_date += timedelta(days=1)
            last_time = calling_point_time
            calling_point[event] = datetime.combine(activation_date, calling_point_time)
        return activation_date, last_time

    def _calling_point_sort_key(self, activation):
        return activation['arrival'] or datetime.min.replace(tzinfo=utc)

    @property
    def _schedule_collection(self):
        if self._kv_schedule_collection is None:
            self._kv_schedule_collection = self._kv_store.db.schedules
            self._kv_schedule_collection.ensure_index('source')
            self._kv_schedule_collection.ensure_index('schedule_expires', expire_after_seconds=48 * 60 * 60)
        return self._kv_schedule_collection

    @property
    def _activations_collection(self):
        if self._kv_activations_collection is None:
            self._kv_activations_collection = self._kv_store.db.activations
            self._kv_activations_collection.ensure_index('activated_on', expire_after_seconds=36 * 60 * 60)
            self._kv_activations_collection.ensure_index('activation_id')
            self._kv_activations_collection.ensure_index({'public_departure': ASCENDING,
                                                          'predicted_departure': ASCENDING,
                                                          'tiploc': ASCENDING,
                                                          'state': ASCENDING,
                                                          'activation_id': ASCENDING,
                                                          'service_type': ASCENDING}.items())
            self._kv_activations_collection.ensure_index({'public_departure': ASCENDING,
                                                          'predicted_departure': ASCENDING,
                                                          'atoc': ASCENDING,
                                                          'state': ASCENDING,
                                                          'activation_id': ASCENDING,
                                                          'service_type': ASCENDING}.items())
            self._kv_activations_collection.ensure_index({'activation_id': ASCENDING,
                                                          'service_type': ASCENDING,
                                                          'arrival': ASCENDING,
                                                          'departure': ASCENDING,
                                                          'state': ASCENDING}.items())
        return self._kv_activations_collection
