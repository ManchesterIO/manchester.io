from flask import Flask
from flask.ext.pymongo import PyMongo
from raven.contrib.celery import register_signal, register_logger_signal
from raven.contrib.flask import Sentry

from medlock.endpoints.search import SearchResults
from medlock.helpers.float_converter import NegativeFloatConverter
from medlock.importers.naptan import NaptanImporter
from medlock.importers.network_rail import NetworkRailScheduleImporter
from medlock.scheduler import Celery
from medlock.services.importer_metadata import ImporterMetadataFactory
from medlock.services.locations import LocationService
from medlock.services.schedules import ScheduleService

app = Flask('medlock')
app.config.from_envvar('CONFIG')

mongo = PyMongo(app)

sentry = Sentry(app)

celery = Celery(app)
register_signal(sentry.client)
register_logger_signal(sentry.client)

location_service = LocationService(mongo)
schedule_service = ScheduleService(mongo)
metadata_factory = ImporterMetadataFactory(mongo)

naptan_importer = NaptanImporter(location_service,
                                 metadata_factory.build('naptan'),
                                 ['910', '940', 'MA'])

network_rail_schedule_importer = NetworkRailScheduleImporter(schedule_service,
                                                             metadata_factory.build('network-rail-schedule'),
                                                             app.config['NETWORK_RAIL_AUTH'])

app.url_map.converters['float'] = NegativeFloatConverter

SearchResults(app, location_service).init()


def import_naptan():
    with app.app_context():
        naptan_importer.load()
celery.task(import_naptan, crontab=naptan_importer.IMPORT_SCHEDULE)


def import_network_rail_schedule():
    with app.app_context():
        network_rail_schedule_importer.load()
celery.task(import_network_rail_schedule, crontab=network_rail_schedule_importer.IMPORT_SCHEDULE)


if __name__ == '__main__':
    app.debug = True
    app.run(port=8010)
