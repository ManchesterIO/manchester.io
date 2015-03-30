from cStringIO import StringIO
from datetime import timedelta, datetime
from gzip import GzipFile
import logging
from xml.etree import cElementTree as ET

from celery.schedules import schedule
from stomp.listener import ConnectionListener
from medlock.parsers.darwin import DarwinPushPortParser

LOGGER = logging.getLogger(__name__)


class DarwinPushPortImporter(ConnectionListener):

    CLEANUP_SCHEDULE = schedule(run_every=timedelta(days=1))

    def __init__(self, app, statsd, schedule_service, mq):
        self._app = app
        self._schedule_service = schedule_service
        self._mq = mq
        self._parser = DarwinPushPortParser()

    def on_message(self, headers, message):
        body = ET.fromstring(GzipFile(fileobj=StringIO(message)).read())
        for event_type, event_body in self._parser.parse(body):
            if event_type == 'activation':
                self._handle_activation(event_body)

        self._mq.ack(id=headers['message-id'], subscription=headers['subscription'])

    def _handle_activation(self, (activation_id, schedule)):
        with self._app.app_context():
            LOGGER.info("Activated %s", activation_id)
            self._schedule_service.insert(**schedule)
            self._schedule_service.activate_schedule(
                activation_id=activation_id,
                service_type='train',
                activation_date=datetime.strptime(schedule['schedule_start'], '%Y-%m-%d'),
                service_id=schedule['service_id'],
                schedule_start=schedule['schedule_start']
            )

    def cleanup(self):
        pass
