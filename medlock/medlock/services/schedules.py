from datetime import timedelta, datetime, time
import logging

from pymongo import ASCENDING

LOGGER = logging.getLogger(__name__)


class ScheduleService(object):

    ARRIVAL_EVENT = 'arrival'
    DEPARTURE_EVENT = 'departure'

    def __init__(self, mongo):
        self._kv_store = mongo
        self._kv_schedule_collection = None
        self._kv_association_collection = None
        self._kv_activations_collection = None

    def insert(self, **kwargs):
        self._schedule_collection.insert(kwargs)

    def delete(self, **kwargs):
        self._schedule_collection.remove(kwargs)

    def create_association(self, **kwargs):
        self._association_collection.insert(kwargs)

    def delete_association(self, **kwargs):
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

    def activate_schedule(self, activation_id, activation_date, service_id, schedule_start):
        schedule = self._get_schedule_to_activate(service_id, schedule_start)
        if schedule:
            self._create_activation(activation_id, activation_date, schedule)
            return True
        else:
            return False

    def update_activation(self, activation_id, calling_point_planned_timestamp, event, actual_timestamp):
        if event == self.ARRIVAL_EVENT:
            query_field = 'calling_points.arrival'
            update_field = 'calling_points.$.actual_arrival'
        elif event == self.DEPARTURE_EVENT:
            query_field = 'calling_points.departure'
            update_field = 'calling_points.$.actual_departure'
        else:
            LOGGER.error("Attempted to update activation %s with invalid event %s", activation_id, event)
            return False

        result = self._activations_collection.update(
            {'activation_id': activation_id, query_field: calling_point_planned_timestamp},
            {'$set': { update_field: actual_timestamp}}
        )
        if not result['updatedExisting']:
            if self._activations_collection.find({'activation_id': activation_id}).count() > 0:
                return False
            else:
                return None
        else:
            return True


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

    def _create_activation(self, activation_id, activation_time, schedule):
        activation = {
            'activated_on': activation_time,
            'calling_points': []
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
                'predicted_platform': None,
                'cancelled': None
            })
            activation['calling_points'].append(calling_point)

        self._activations_collection.update({'activation_id': activation_id},
                                            {'$set': activation},
                                            upsert=True)

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
            self._kv_activations_collection.ensure_index('activated_on')
        return self._kv_activations_collection
