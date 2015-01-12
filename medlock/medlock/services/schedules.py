from pymongo import ASCENDING


class ScheduleService(object):

    def __init__(self, mongo):
        self._kv_store = mongo
        self._kv_schedule_collection = None
        self._kv_association_collection = None

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

    @property
    def _schedule_collection(self):
        if self._kv_schedule_collection is None:
            self._kv_schedule_collection = self._kv_store.db.schedules
            self._kv_schedule_collection.ensure_index('source')
            self._kv_schedule_collection.ensure_index({'service_id': ASCENDING,
                                                       'schedule_priority': ASCENDING,
                                                       'schedule_start': ASCENDING,
                                                       'source': ASCENDING}.items(),
                                                      name='schedule_delete_lookup')
        return self._kv_schedule_collection

    @property
    def _association_collection(self):
        if self._kv_association_collection is None:
            self._kv_association_collection = self._kv_store.db.associations
            self._kv_association_collection.ensure_index('source')
            self._kv_association_collection.ensure_index({'service_id': ASCENDING,
                                                          'schedule_priority': ASCENDING,
                                                          'association_start': ASCENDING,
                                                          'source': ASCENDING,
                                                          'associated_service_id': ASCENDING,
                                                          'associated_location': ASCENDING}.items(),
                                                         name='association_delete_lookup')
        return self._kv_association_collection
