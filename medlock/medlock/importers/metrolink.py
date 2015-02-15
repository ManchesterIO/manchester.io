from datetime import date, datetime, timedelta
import logging
from celery.schedules import schedule

LOGGER = logging.getLogger(__name__)

class MetrolinkRunningDataImporter(object):

    IMPORT_SCHEDULE = schedule(run_every=timedelta(hours=2))
    TICK_SCHEDULE = schedule(run_every=timedelta(minutes=1))

    def __init__(self, schedule_service):
        self._schedule_service = schedule_service

    def activate(self):
        """
        This does a bulk activation of all schedules for today
        """
        for schedule in self._schedule_service.fetch_valid_schedules_for(date.today(),
                                                                         service_type='metrolink',
                                                                         bank_holiday=False,
                                                                         school_holiday=False):
            activation_id = '{service_id}.{day}'.format(service_id=schedule['service_id'], day=date.today().day)
            if len(self._schedule_service.fetch_activation(activation_id, 'metrolink')['calling_points']) == 0:
                LOGGER.info("Activating {activation_id}".format(activation_id=activation_id))
                self._schedule_service.activate_schedule(activation_id,
                                                         'metrolink',
                                                         datetime.now(),
                                                         schedule['service_id'],
                                                         schedule['schedule_start'])

    def on_tick(self):
        self._schedule_service.bulk_manual_update('departure', datetime.now(), 'metrolink')
