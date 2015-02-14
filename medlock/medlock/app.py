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
from medlock.importers.naptan import NaptanImporter
from medlock.importers.network_rail_real_time import NetworkRailRealTimeImporter
from medlock.importers.network_rail_schedule import NetworkRailScheduleImporter
from medlock.importers.network_rail_vstp import NetworkRailVstpImporter
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

mq = stomp.Connection(host_and_ports=[('datafeeds.networkrail.co.uk', 61618)],
                      keepalive=True,
                      vhost='datafeeds.networkrail.co.uk',
                      heartbeats=(10000, 5000))

location_service = LocationService(statsd, mongo)
schedule_service = ScheduleService(statsd, mongo)
metadata_factory = ImporterMetadataFactory(mongo)

naptan_importer = NaptanImporter(location_service,
                                 metadata_factory.build('naptan'),
                                 ['910', '940', 'MA'])

network_rail_schedule_importer = NetworkRailScheduleImporter(schedule_service,
                                                             metadata_factory.build('network-rail-schedule'),
                                                             app.config['NETWORK_RAIL_AUTH'])

network_rail_vstp_importer = NetworkRailVstpImporter(app, statsd, schedule_service, mq)
mq.set_listener('vstp', network_rail_vstp_importer)

network_rail_real_time_importer = NetworkRailRealTimeImporter(app, statsd, schedule_service, mq)
mq.set_listener('movements', network_rail_real_time_importer)


def import_naptan():
    with app.app_context():
        naptan_importer.load()
celery.task(import_naptan, crontab=naptan_importer.IMPORT_SCHEDULE)


def import_network_rail_schedule():
    with app.app_context():
        network_rail_schedule_importer.load()
celery.task(import_network_rail_schedule, crontab=network_rail_schedule_importer.IMPORT_SCHEDULE)

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
