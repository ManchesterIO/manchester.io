import os

from flask import Flask
from flask.ext.pymongo import PyMongo

from medlock.services.importer_metadata import ImporterMetadataFactory
from medlock.services.locations import LocationService
from medlock.importers.naptan import NaptanImporter

app = Flask(__name__.split('.')[0])
app.debug = os.environ.get('DEBUG', 'false') == 'true'

mongo = PyMongo(app)
location_service = LocationService(mongo)
metadata_factory = ImporterMetadataFactory(mongo)
naptan_importer = NaptanImporter(location_service,
                                 metadata_factory.build('naptan'),
                                 ['180', '910', '940', 'MA'])


if __name__ == '__main__':
    app.run()
