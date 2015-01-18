import logging
from datetime import time, timedelta

LOGGER = logging.getLogger(__name__)


class NetworkRailScheduleParser(object):

    _ASSOCIATION_CATEGORIES = {
        'JJ': 'join',
        'VV': 'split'
    }

    def __init__(self, schedule_service, source):
        self._schedule_service = schedule_service
        self._source = source

    def parse(self, schedule_json):
        for schedule in schedule_json:
            if 'JsonAssociationV1' in schedule:
                self._handle_association(schedule['JsonAssociationV1'])
            elif 'JsonScheduleV1' in schedule:
                self._handle_schedule(schedule['JsonScheduleV1'])
            elif self.is_vstp_message(schedule):
                self._handle_vstp(schedule['VSTPCIFMsgV1']['schedule'])

    def is_vstp_message(self, message):
        return 'VSTPCIFMsgV1' in message

    def _handle_association(self, association):
        if association['transaction_type'] == 'Delete':
            self._schedule_service.delete_association(
                service_id=association['main_train_uid'],
                schedule_priority=association['CIF_stp_indicator'],
                association_start=association['assoc_start_date'][:10],
                source=self._source,
                associated_service_id=association['assoc_train_uid'],
                associated_location=association['location']
            )
        elif association['transaction_type'] == 'Create':
            if association['category'] in self._ASSOCIATION_CATEGORIES:
                self._schedule_service.create_association(
                    service_id=association['main_train_uid'],
                    schedule_priority=association['CIF_stp_indicator'],
                    association_start=association['assoc_start_date'][:10],
                    association_end=association['assoc_end_date'][:10],
                    association_type=self._ASSOCIATION_CATEGORIES[association['category']],
                    source=self._source,
                    associated_service_id=association['assoc_train_uid'],
                    associated_location=association['location']
                )
        else:
            LOGGER.error("Encountered unexpected transaction_type %s: %s",
                         association['transaction_type'], str(association))

    def _handle_schedule(self, schedule):
        if schedule['transaction_type'] == 'Delete':
            LOGGER.info("Deleting schedule for %s", schedule['CIF_train_uid'])
            self._schedule_service.delete(service_id=schedule['CIF_train_uid'],
                                          schedule_priority=schedule['CIF_stp_indicator'],
                                          schedule_start=schedule['schedule_start_date'],
                                          source=self._source)
        elif schedule['transaction_type'] == 'Create':
            if self._is_passenger_train(schedule['schedule_segment']['CIF_train_category']):
                LOGGER.info("Inserting schedule for %s", schedule['CIF_train_uid'])
                self._schedule_service.insert(source=self._source, **self._build_schedule(schedule, vstp=False))
        else:
            LOGGER.error("Encountered unexpected transaction_type %s: %s", schedule['transaction_type'], str(schedule))

    def _handle_vstp(self, schedule):
        if schedule['transaction_type'] == 'Delete':
            LOGGER.info("Deleting schedule for %s", schedule['CIF_train_uid'])
            self._schedule_service.delete(service_id=schedule['CIF_train_uid'],
                                          schedule_priority=schedule['CIF_stp_indicator'],
                                          schedule_start=schedule['schedule_start_date'],
                                          source=self._source)
        elif schedule['transaction_type'] == 'Create':
            if self._is_passenger_train(schedule['schedule_segment'][0]['CIF_train_category']):
                LOGGER.info("Inserting schedule for %s", schedule['CIF_train_uid'])
                self._schedule_service.insert(source=self._source, **self._build_schedule(schedule, vstp=True))
        else:
            LOGGER.error("Encountered unexpected transaction_type %s: %s", schedule['transaction_type'], str(schedule))

    def _is_passenger_train(self, category):
        return category is not None and (category[:1] in ['O', 'X'] or category in ['BR', 'BS'])

    def _build_schedule(self, service, vstp):
        schedule = {
            'service_id': service['CIF_train_uid'],
            'schedule_priority': service['CIF_stp_indicator'],
            'schedule_start': service['schedule_start_date'],
            'schedule_expires': service['schedule_end_date']
        }

        if vstp:
            schedule['calling_points'] = map(self._build_vstp_calling_point,
                                             service['schedule_segment'][0]['schedule_location'])
        else:
            schedule['calling_points'] = map(self._build_calling_point,
                                             service['schedule_segment']['schedule_location'])

        return schedule

    def _build_calling_point(self, location):
        if location.get('pass') is not None:
            arrival = location['pass']
            departure = location['pass']
        else:
            arrival = location.get('arrival')
            departure = location.get('departure')

        arrival = self._convert_half_minutes(arrival)
        departure = self._convert_half_minutes(departure)

        return {
            'tiploc': location['tiploc_code'],
            'platform': location['platform'],
            'public_arrival': location.get('public_arrival'),
            'public_departure': location.get('public_departure'),
            'arrival': arrival,
            'departure': departure,
            'allowances': 0
        }

    def _convert_half_minutes(self, call_time):
        if call_time is not None and call_time[-1] == 'H':
            call_time = call_time[:-1] + '30'
        return call_time

    def _build_vstp_calling_point(self, location):
        pass_time = self._convert_vstp_time(location['scheduled_pass_time'])

        if pass_time is not None:
            arrival = pass_time
            departure = pass_time
            public_arrival = None
            public_departure = None
        else:
            arrival = self._convert_vstp_time(location['scheduled_arrival_time'])
            departure = self._convert_vstp_time(location['scheduled_departure_time'])
            public_arrival = self._convert_wtt_to_public(arrival)
            public_departure = self._convert_wtt_to_public(departure)

        return {
            'tiploc': location['location']['tiploc']['tiploc_id'],
            'platform': location['CIF_platform'].strip(),
            'public_arrival': public_arrival,
            'public_departure': public_departure,
            'arrival': arrival,
            'departure': departure,
            'allowances': 0
        }

    def _convert_vstp_time(self, call_time):
        if call_time.strip() == '':
            return None
        else:
            return call_time

    def _convert_wtt_to_public(self, call_time):
        if call_time is not None:
            call_time = time(int(call_time[:2]), int(call_time[2:4]), int(call_time[4:6]))
            if call_time.second == 30:
                call_time += timedelta(seconds=30)
            return call_time.strftime('%H%M')
        else:
            return None
