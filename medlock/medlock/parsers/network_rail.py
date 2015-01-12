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
            if self._is_passenger_train(schedule):
                LOGGER.info("Inserting schedule for %s", schedule['CIF_train_uid'])
                self._schedule_service.insert(source=self._source, **self._build_schedule(schedule))
        else:
            LOGGER.error("Encountered unexpected transaction_type %s: %s", schedule['transaction_type'], str(schedule))

    def _is_passenger_train(self, schedule):
        category = schedule['schedule_segment']['CIF_train_category']
        return category is not None and (category[:1] in ['O', 'X'] or category in ['BR', 'BS'])

    def _build_schedule(self, schedule):
        return {
            'service_id': schedule['CIF_train_uid'],
            'schedule_priority': schedule['CIF_stp_indicator'],
            'schedule_start': schedule['schedule_start_date'],
            'schedule_expires': schedule['schedule_end_date'],
            'calling_points': map(self._build_calling_point,
                                  filter(self._is_passenger_calling_point,
                                         schedule['schedule_segment']['schedule_location']))
        }

    def _is_passenger_calling_point(self, location):
        return location.get('pass') is None

    def _build_calling_point(self, location):
        return {
            'tiploc': location['tiploc_code'],
            'platform': location['platform'],
            'arrival': location.get('public_arrival'),
            'departure': location.get('public_departure')
        }
