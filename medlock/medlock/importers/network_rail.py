from datetime import timedelta, date, datetime
import gzip
import json
import logging
import os
from tempfile import NamedTemporaryFile

from celery.exceptions import Retry
from celery.schedules import crontab
import requests

LOGGER = logging.getLogger(__name__)


class NetworkRailScheduleImporter(object):

    IMPORT_SCHEDULE = crontab(hour=6, minute=0)

    _FULL_URL = 'https://datafeeds.networkrail.co.uk/ntrod/CifFileAuthenticate?type=CIF_ALL_FULL_DAILY&day=toc-full'
    _DAY_URL = 'https://datafeeds.networkrail.co.uk/ntrod/CifFileAuthenticate?type=CIF_ALL_UPDATE_DAILY&day=toc-update-{}'

    def __init__(self, schedule_service, metadata, network_rail_auth):
        self._schedule_service = schedule_service
        self._metadata = metadata
        self._network_rail_auth = network_rail_auth

    def load(self):
        last_import = self._metadata.get('last-import-date')
        if last_import is not None:
            last_import = date.fromtimestamp(last_import)
        if last_import is None or date.today() - last_import > timedelta(days=7):
            LOGGER.error("Unable to find an appropriate partial update, falling back to full")
            self._full_update()
        else:
            day_to_import = last_import + timedelta(days=1)
            while day_to_import < date.today():
                self._day_update(day_to_import)
                day_to_import += timedelta(days=1)

    def _full_update(self):
        schedule = self._fetch_json(self._FULL_URL)
        timestamp = schedule.next()['JsonTimetableV1']['timestamp']

        self._schedule_service.delete(source='nrod-schedule')

        self._metadata['last-import-date'] = timestamp

    def _day_update(self, expected_date):
        LOGGER.info("Starting Network Rail partial update for %s", expected_date)
        day = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][expected_date.weekday()]
        schedule = self._fetch_json(self._DAY_URL.format(day))
        timestamp = schedule.next()['JsonTimetableV1']['timestamp']
        schedule_date = date.fromtimestamp(int(timestamp))

        if schedule_date != expected_date:
            LOGGER.error("Looking for update file for %s, but got %s", expected_date, schedule_date)
            raise Retry('Network Rail file might be late', when=datetime.now() + timedelta(hours=1))

        self._metadata['last-import-date'] = timestamp

    def _fetch_json(self, url):
        tmp = NamedTemporaryFile(delete=False)
        try:
            # TODO: Add SSL verify back in when NROD sort out their SSL cert.
            response = requests.get(url, timeout=5, stream=True, auth=self._network_rail_auth, verify=False)
            for chunk in response.iter_content(chunk_size=512):
                tmp.write(chunk)
            tmp.close()

            for line in gzip.open(tmp.name):
                yield json.loads(line)

        finally:
            if not tmp.closed:
                tmp.close()
            os.unlink(tmp.name)
