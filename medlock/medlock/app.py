import os

from flask import Flask
from flask.ext.pymongo import PyMongo
from raven.contrib.celery import register_signal

from medlock.endpoints.search import SearchResults
from medlock.helpers.float_converter import NegativeFloatConverter
from medlock.importers.naptan import NaptanImporter
from medlock.scheduler import Celery
from medlock.services.importer_metadata import ImporterMetadataFactory
from medlock.services.locations import LocationService

app = Flask('medlock')
app.debug = os.environ.get('DEBUG', 'false') == 'true'
app.config.update({
    'CELERYBEAT_SCHEDULE_FILENAME': "/srv/manchester.io/data/celery-schedule"
})

mongo = PyMongo(app)

celery = Celery(app)
register_signal(celery)

location_service = LocationService(mongo)
metadata_factory = ImporterMetadataFactory(mongo)
naptan_importer = NaptanImporter(location_service,
                                 metadata_factory.build('naptan'),
                                 ['910', '940', 'MA'])
celery.periodic_task(naptan_importer.load, crontab=naptan_importer.IMPORT_SCHEDULE)

app.url_map.converters['float'] = NegativeFloatConverter

SearchResults(app, location_service).init()

if __name__ == '__main__':
    app.debug = True
    app.run(port=8010)
