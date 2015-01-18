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

    def __init__(self, app, statsd, schedule_service, mq):
        self._app = app
        self._schedule_service = schedule_service
        self._mq = mq
        self._statsd = statsd

    def on_message(self, headers, message):
        if headers['destination'] == '/topic/TRAIN_MVT_ALL_TOC':
            try:
                body = json.loads(message)
            except ValueError:
                self._statsd.incr(__name__ + '.messages.failed_json_parse')
                LOGGER.exception("Failed to decode JSON in Network Rail feed")
            else:
                self._statsd.incr(__name__ + '.messages.raw')
                for movement in body:
                    self._handle_message(movement)
                self._mq.ack(id=headers['message-id'], subscription=headers['subscription'])

    def _handle_message(self, movement):
        try:
            if movement['header']['msg_type'] == '0001':
                self._statsd.incr(__name__ + '.messages.activation')
                self._handle_activation(movement['body'])
            elif movement['header']['msg_type'] == '0003':
                self._statsd.incr(__name__ + '.messages.movement')
                self._handle_movement(movement['body'])
            else:
                self._statsd.incr(__name__ + '.messages.unknown')
        except:
            self._statsd.incr(__name__ + '.handler_exception')
            LOGGER.exception("Failed to handle a movement message")

    def _handle_activation(self, body):
        with self._app.app_context():
            activation_successful = self._schedule_service.activate_schedule(
                body['train_id'],
                datetime.fromtimestamp(int(body['origin_dep_timestamp']) / 1000),
                body['train_uid'],
                body['schedule_start_date'])

            if activation_successful:
                self._statsd.incr(__name__ + '.activations.hit')
                LOGGER.info("Activated %s as %s", body['train_uid'], body['train_id'])
            else:
                self._statsd.incr(__name__ + '.activations.miss')
                LOGGER.info("Failed to activate %s as %s", body['train_uid'], body['train_id'])

    def _handle_movement(self, body):
        with self._app.app_context():
            if body['variation_status'] != 'OFF ROUTE':
                movement_successful = self._schedule_service.update_activation(
                    body['train_id'],
                    datetime.fromtimestamp(int(body['planned_timestamp']) / 1000),
                    self._EVENTS.get(body['event_type']),
                    datetime.fromtimestamp(int(body['actual_timestamp']) / 1000))

                if movement_successful is True:
                    self._statsd.incr(__name__ + '.movements.update_success')
                    LOGGER.info("Recorded %s for %s at %s", body['event_type'], body['train_id'], body['loc_stanox'])
                elif movement_successful is False:
                    self._statsd.incr(__name__ + '.movements.update_failed')
                    LOGGER.info("Failed to record %s for %s at %s", body['event_type'], body['train_id'], body['loc_stanox'])
                else:
                    self._statsd.incr(__name__ + '.movements.missing_activation')
            else:
                self._statsd.incr(__name__ + '.movements.off_route')

