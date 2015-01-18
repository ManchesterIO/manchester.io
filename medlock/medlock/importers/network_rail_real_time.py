import json
import logging
from datetime import datetime
from medlock.services.schedules import ScheduleService


LOGGER = logging.getLogger(__name__)


class NetworkRailRealTimeImporter(object):

    _EVENTS = {
        'ARRIVAL': ScheduleService.ARRIVAL_EVENT,
        'DEPARTURE': ScheduleService.DEPARTURE_EVENT
    }

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
                    self._handle_message(movement)
                self._mq.ack(id=headers['message-id'], subscription=headers['subscription'])

    def _handle_message(self, movement):
        try:
            if movement['header']['msg_type'] == '0001':
                self._handle_activation(movement['body'])
            elif movement['header']['msg_type'] == '0003':
                self._handle_movement(movement['body'])
        except:
            LOGGER.exception("Failed to handle a movement message")

    def _handle_activation(self, body):
        with self._app.app_context():
            activation_successful = self._schedule_service.activate_schedule(
                body['train_id'],
                datetime.fromtimestamp(int(body['origin_dep_timestamp']) / 1000),
                body['train_uid'],
                body['schedule_start_date'])

            if activation_successful:
                LOGGER.info("Activated %s as %s", body['train_uid'], body['train_id'])
            else:
                LOGGER.info("Failed to activate %s as %s", body['train_uid'], body['train_id'])

    def _handle_movement(self, body):
        with self._app.app_context():
            if body['variation_status'] != 'OFF ROUTE':
                movement_successful = self._schedule_service.update_activation(
                    body['train_id'],
                    datetime.fromtimestamp(int(body['planned_timestamp']) / 1000),
                    self._EVENTS.get(body['event_type']),
                    datetime.fromtimestamp(int(body['actual_timestamp']) / 1000))
            else:
                movement_successful = None

            if movement_successful is True:
                LOGGER.info("Recorded %s for %s at %s", body['event_type'], body['train_id'], body['loc_stanox'])
            elif movement_successful is False:
                LOGGER.info("Failed to record %s for %s at %s", body['event_type'], body['train_id'], body['loc_stanox'])
