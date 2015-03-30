import logging
from flask import Flask
from flask.ext.pymongo import PyMongo
from flask.ext.statsd import StatsD
from raven.contrib.celery import register_signal, register_logger_signal
from raven.contrib.flask import Sentry
import stomp

from medlock.endpoints.search import SearchResults
from medlock.endpoints.services import Services
from medlock.endpoints.stations import Stations
from medlock.helpers.float_converter import NegativeFloatConverter
from medlock.importers.darwin_push_port import DarwinPushPortImporter
from medlock.importers.gmpte_cif import CifImporter
from medlock.importers.metrolink import MetrolinkRunningDataImporter
from medlock.importers.naptan import NaptanImporter
from medlock.scheduler import Celery
from medlock.services.importer_metadata import ImporterMetadataFactory
from medlock.services.locations import LocationService
from medlock.services.schedules import ScheduleService

app = Flask('medlock')
app.config.from_envvar('CONFIG')

mongo = PyMongo(app)

sentry = Sentry(app, logging=True, level=logging.WARNING)

celery = Celery(app)
register_signal(sentry.client)
register_logger_signal(sentry.client)

statsd = StatsD(app)

mq = stomp.Connection(host_and_ports=[('datafeeds.nationalrail.co.uk', 61613)],
                      keepalive=True,
                      vhost='datafeeds.nationalrail.co.uk',
                      heartbeats=(10000, 5000))

location_service = LocationService(statsd, mongo)
schedule_service = ScheduleService(statsd, mongo)
metadata_factory = ImporterMetadataFactory(mongo)

naptan_importer = NaptanImporter(location_service,
                                 metadata_factory.build('naptan'),
                                 ['910', '940', 'MA'])

tfgm_schedule_importer = CifImporter(schedule_service, metadata_factory.build('tfgm-schedule'))

metrolink_running_data_importer = MetrolinkRunningDataImporter(schedule_service)

darwin_push_port_importer = DarwinPushPortImporter(app, statsd, schedule_service, mq)
mq.set_listener('darwin', darwin_push_port_importer)


def cleanup_darwin():
    with app.app_context():
        darwin_push_port_importer.cleanup()
celery.task(cleanup_darwin, crontab=darwin_push_port_importer.CLEANUP_SCHEDULE)


def import_naptan():
    with app.app_context():
        naptan_importer.load()
celery.task(import_naptan, crontab=naptan_importer.IMPORT_SCHEDULE)


def import_tfgm_schedule():
    with app.app_context():
        tfgm_schedule_importer.load()
celery.task(import_tfgm_schedule, crontab=tfgm_schedule_importer.IMPORT_SCHEDULE)


def activate_metrolink():
    with app.app_context():
        metrolink_running_data_importer.activate()
celery.task(activate_metrolink, crontab=metrolink_running_data_importer.IMPORT_SCHEDULE)


def tick_metrolink():
    with app.app_context():
        metrolink_running_data_importer.on_tick()
celery.task(tick_metrolink, crontab=metrolink_running_data_importer.TICK_SCHEDULE)

app.url_map.converters['float'] = NegativeFloatConverter

SearchResults(app, statsd, location_service).init()
Services(app, statsd, location_service, schedule_service).init()
Stations(app, statsd, location_service, schedule_service).init()

if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s'))
    logging.getLogger().addHandler(console)
    logging.getLogger('medlock').setLevel(logging.INFO)

    app.debug = True
    app.run(port=8010)
