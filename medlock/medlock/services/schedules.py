class ScheduleService(object):

    def __init__(self, mongo):
        self._kv_store = mongo
        self._kv_collection = None

    def reset(self, source):
        self._collection.remove({'source': source})

    @property
    def _collection(self):
        if self._kv_collection is None:
            self._kv_collection = self._kv_store.db.schedules
            self._kv_collection.ensure_index('source')
        return self._kv_collection
