import json
import logging

from medlock.parsers.network_rail import NetworkRailScheduleParser

LOGGER = logging.getLogger(__name__)


class NetworkRailVstpImporter(object):

    def __init__(self, schedule_service, mq):
        self._parser = NetworkRailScheduleParser(schedule_service, source='nrod-vstp')
        self._mq = mq

    def on_message(self, headers, message):
        try:
            body = json.loads(message)
        except ValueError:
            LOGGER.exception("Failed to decode JSON in Network Rail feed")
        else:
            if self._is_vstp_message(body):
                self._parser.parse([{'JsonScheduleV1': body['VSTPCIFMsgV1']['schedule']}])
                self._mq.ack(id=headers['message-id'], subscription=headers['subscription'])

    def _is_vstp_message(self, body):
        return 'VSTPCIFMsgV1' in body
