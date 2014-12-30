class ImporterMetadataFactory(object):

    def __init__(self, kv_store):
        self._kv_store = kv_store
        self._importer_metadata = None

    def build(self, importer):
        return ImporterMetadata(self._kv_store, importer)


class ImporterMetadata(object):

    def __init__(self, kv_store, importer_key):
        self._kv_store = kv_store
        self._kv_collection = None
        self._importer_key = importer_key

    def get(self, key, default=None):
        result = self._collection.find_one({'importer': self._importer_key})
        if result is None:
            result = {}

        return result.get(key, default)

    def __setitem__(self, key, value):
        self._collection.update({'importer': self._importer_key},
                        {'$set': {key: value}},
                        upsert=True)

    @property
    def _collection(self):
        if self._kv_collection is None:
            self._kv_collection = self._kv_store.db.importer_metadata
            self._kv_collection.ensure_index('importer')
        return self._kv_collection

