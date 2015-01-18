import json
import logging

from medlock.parsers.network_rail import NetworkRailScheduleParser

LOGGER = logging.getLogger(__name__)


class NetworkRailVstpImporter(object):

    def __init__(self, app, statsd, schedule_service, mq):
        self._app = app
        self._parser = NetworkRailScheduleParser(schedule_service, source='nrod-vstp')
        self._mq = mq
        self._statsd = statsd

    def on_message(self, headers, message):
        try:
            body = json.loads(message)
        except ValueError:
            self._statsd.incr(__name__ + '.failed_json_parse')
            LOGGER.exception("Failed to decode JSON in Network Rail feed")
        else:
            if self._parser.is_vstp_message(body):
                self._statsd.increment(__name__ + '.vstp_message')
                with self._app.app_context():
                    try:
                        self._parser.parse([body])
                    except:
                        self._statsd.increment(__name__ + '.vstp_message_failed')
                        LOGGER.exception("Failed to handle a VSTP message")
                self._mq.ack(id=headers['message-id'], subscription=headers['subscription'])
