import logging

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
                                             filter(self._is_passenger_calling_point(vstp),
                                                    service['schedule_segment'][0]['schedule_location']))
        else:
            schedule['calling_points'] = map(self._build_calling_point,
                                             filter(self._is_passenger_calling_point(vstp),
                                                    service['schedule_segment']['schedule_location']))

        return schedule

    def _is_passenger_calling_point(self, vstp):
        if vstp:
            return lambda location: location.get('scheduled_pass_time', '').strip() == ''
        else:
            return lambda location: location.get('pass') is None

    def _build_calling_point(self, location):
        return {
            'tiploc': location['tiploc_code'],
            'platform': location['platform'],
            'arrival': location.get('public_arrival'),
            'departure': location.get('public_departure')
        }

    def _build_vstp_calling_point(self, location):
        calling_point = {
            'tiploc': location['location']['tiploc']['tiploc_id'],
            'platform': location['CIF_platform'].strip(),
            'arrival': location['scheduled_arrival_time'][:4],
            'departure': location['public_departure_time'][:4]
        }
        if calling_point['arrival'].strip() == '':
            calling_point['arrival'] = None
        if calling_point['departure'].strip() == '':
            calling_point['departure'] = None
        return calling_point
