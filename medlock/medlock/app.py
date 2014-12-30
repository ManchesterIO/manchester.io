import os

from flask import Flask
from flask.ext.pymongo import PyMongo
from raven.contrib.celery import register_signal

from medlock.scheduler import Celery
from medlock.importers.naptan import NaptanImporter
from medlock.services.importer_metadata import ImporterMetadataFactory
from medlock.services.locations import LocationService

app = Flask(__name__.split('.')[0])
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
                                 ['180', '910', '940', 'MA'])
celery.periodic_task(naptan_importer.load, crontab=naptan_importer.IMPORT_SCHEDULE)

if __name__ == '__main__':
    app.run()
