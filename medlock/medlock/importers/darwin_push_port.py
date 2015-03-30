from cStringIO import StringIO
from datetime import timedelta, datetime, date
from gzip import GzipFile
import logging
from xml.etree.cElementTree import fromstring, ParseError

from celery.schedules import schedule
from stomp.listener import ConnectionListener
from medlock.parsers.darwin import DarwinPushPortParser

LOGGER = logging.getLogger(__name__)


class DarwinPushPortImporter(ConnectionListener):

    CLEANUP_SCHEDULE = schedule(run_every=timedelta(days=1))

    def __init__(self, app, statsd, schedule_service, mq):
        self._app = app
        self._statsd = statsd
        self._schedule_service = schedule_service
        self._mq = mq
        self._parser = DarwinPushPortParser(statsd)

    def on_message(self, headers, message):
        try:
            body = self._parse_message(message)
        except ParseError:
            self._statsd.incr(__name__ + '.xml_parse_error')
        except IOError:
            self._statsd.incr(__name__ + '.gzip_error')
        else:
            self._handle_response(body)
            self._mq.ack(id=headers['message-id'], subscription=headers['subscription'])

    def cleanup(self):
        self._schedule_service.remove_expired(date.today(), 'darwin')

    def _parse_message(self, message):
        return fromstring(GzipFile(fileobj=StringIO(message)).read())

    def _handle_response(self, body):
        for event_type, event_body in self._parser.parse(body):
            if event_type == 'activation':
                self._handle_activation(event_body)
            elif event_type == 'deactivation':
                self._handle_deactivation(event_body)
            elif event_type == 'status':
                self._handle_status(event_body)
            elif event_type == 'association':
                pass

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

    def _handle_deactivation(self, activation_id):
        LOGGER.info("Deactivated %s", activation_id)
        self._schedule_service.remove_activation(activation_id=activation_id, service_type='train')

    def _handle_status(self, (activation_id, updates)):
        with self._app.app_context():
            for expected, event, actual, actual_or_prediction in updates:
                LOGGER.debug("Updated %s %s %s at %s", activation_id, actual_or_prediction, event, expected)
                self._schedule_service.update_activation(
                    activation_id=activation_id,
                    service_type='train',
                    calling_point_planned_timestamp=expected,
                    event=event,
                    actual_timestamp=actual,
                    actual_or_predicted=actual_or_prediction
                )
