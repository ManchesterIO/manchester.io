from cStringIO import StringIO
from datetime import timedelta
from gzip import GzipFile
import logging
from xml.etree import cElementTree as ET

from celery.schedules import schedule
from stomp.listener import ConnectionListener

LOGGER = logging.getLogger(__name__)


class DarwinPushPortImporter(ConnectionListener):

    CLEANUP_SCHEDULE = schedule(run_every=timedelta(days=1))

    def __init__(self, app, statsd, schedule_service, mq):
        self._mq = mq

    def on_message(self, headers, message):
        body = ET.fromstring(GzipFile(fileobj=StringIO(message)).read())
        self._mq.ack(id=headers['message-id'], subscription=headers['subscription'])
        LOGGER.info(body)

    def cleanup(self):
        pass
