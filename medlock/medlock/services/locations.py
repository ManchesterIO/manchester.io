import logging
import geojson
from pymongo import GEOSPHERE

LOGGER = logging.getLogger(__name__)


class LocationService(object):

    def __init__(self, statsd, kv_store):
        self._statsd = statsd
        self._kv_store = kv_store
        self._kv_collection = None

    def update(self, stop_type, identifier, **kwargs):
        self._statsd.incr(__name__ + '.update')
        self._collection.update({'stop-type': stop_type, 'identifier': identifier},
                                {'$set': kwargs},
                                upsert=True)

    def add_additional_identifier(self, stop_type, identifier, **kwargs):
        if kwargs:
            self._collection.update({'stop-type': stop_type, 'identifier': identifier},
                                    {'$addToSet': kwargs})

    def delete(self, stop_type, identifier):
        self._statsd.incr(__name__ + '.delete')
        self._collection.remove({'stop-type': stop_type, 'identifier': identifier})

    def search_nearby(self, point, stop_type, radius=None):
        self._statsd.incr(__name__ + '.search_nearby_requests')
        query = {
            'location': {'$near': {'$geometry': geojson.GeoJSONEncoder().default(point)}},
            'stop-type': stop_type
        }
        if radius is not None:
            query['location']['$near']['$maxDistance'] = radius
        with self._statsd.timer(__name__ + '.search_nearby_time'):
            return self._collection.find(query)

    @property
    def _collection(self):
        if self._kv_collection is None:
            self._kv_collection = self._kv_store.db.locations
            self._kv_collection.ensure_index('stop-type')
            self._kv_collection.ensure_index('identifier')
            self._kv_collection.ensure_index({'location': GEOSPHERE}.items())
        return self._kv_collection
