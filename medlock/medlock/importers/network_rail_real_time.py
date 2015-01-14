import json
import logging
from datetime import datetime


LOGGER = logging.getLogger(__name__)


class NetworkRailRealTimeImporter(object):

    def __init__(self, app, schedule_service, mq):
        self._app = app
        self._schedule_service = schedule_service
        self._mq = mq

    def on_message(self, headers, message):
        if headers['destination'] == '/topic/TRAIN_MVT_ALL_TOC':
            try:
                body = json.loads(message)
            except ValueError:
                LOGGER.exception("Failed to decode JSON in Network Rail feed")
            else:
                for movement in body:
                    self._handle_movement(movement)
                self._mq.ack(id=headers['message-id'], subscription=headers['subscription'])

    def _handle_movement(self, movement):
        if movement['header']['msg_type'] == '0001':
            self._handle_activation(movement['body'])

    def _handle_activation(self, body):
        with self._app.app_context():
            if self._schedule_service.activate_schedule(body['train_id'],
                                                        datetime.fromtimestamp(int(body['origin_dep_timestamp']) / 1000),
                                                        body['train_uid'],
                                                        body['schedule_start_date']):
                LOGGER.info("Activated %s as %s", body['train_uid'], body['train_id'])
            else:
                LOGGER.info("Failed to activate %s as %s", body['train_uid'], body['train_id'])
