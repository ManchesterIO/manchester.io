import json
import logging

from medlock.parsers.network_rail import NetworkRailScheduleParser

LOGGER = logging.getLogger(__name__)


class NetworkRailVstpImporter(object):

    def __init__(self, app, schedule_service, mq):
        self._app = app
        self._parser = NetworkRailScheduleParser(schedule_service, source='nrod-vstp')
        self._mq = mq

    def on_message(self, headers, message):
        try:
            body = json.loads(message)
        except ValueError:
            LOGGER.exception("Failed to decode JSON in Network Rail feed")
        else:
            if self._parser.is_vstp_message(body):
                with self._app.app_context():
                    self._parser.parse([body])
                self._mq.ack(id=headers['message-id'], subscription=headers['subscription'])
