import logging
import geojson

LOGGER = logging.getLogger(__name__)


class LocationService(object):

    def __init__(self, kv_store):
        self._kv_store = kv_store
        self._kv_collection = None

    def search_nearby(self, point, stop_type, radius):
        query = {
            'location': {'$near': {'$geometry': geojson.GeoJSONEncoder().default(point)}},
            'stop-type': stop_type
        }
        if radius is not None:
            query['location']['$near']['$maxDistance'] = radius
        return self._collection.find(query)

    @property
    def _collection(self):
        if self._kv_collection is None:
            self._kv_collection = self._kv_store.db.locations
            self._kv_collection.ensure_index('slug')
            self._kv_collection.ensure_index({'location': '2dsphere'}.items())
            self._kv_collection.ensure_index('stop-type')
        return self._kv_collection
