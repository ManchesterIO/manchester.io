from datetime import timedelta
import logging
import requests
from tempfile import TemporaryFile
from zipfile import ZipFile

from celery.schedules import schedule
from medlock.parsers.gmpte_cif import CifParser

from medlock.parsers.naptan import NaptanParser

LOGGER = logging.getLogger(__name__)


class CifImporter(object):
    """
    Imports points of interest from the UK's National Public Transport Access Node dataset
    """

    IMPORT_SCHEDULE = schedule(run_every=timedelta(hours=6))

    _CIF_URL = "http://odata.tfgm.com/opendata/downloads/GMPTE_CIF.zip"
    _IMPORTER_VERSION = 1

    def __init__(self, schedule_service, metadata):
        self._metadata = metadata
        self._schedule_service = schedule_service
        self._parser = CifParser(schedule_service)

    def _get_file_from_url(self, temp_file):
        response = requests.get(self._CIF_URL, timeout=5, stream=True)

        if response.headers['etag'] != self._metadata.get('last-etag') \
                or self._IMPORTER_VERSION != self._metadata.get('last-version'):
            LOGGER.info('ETag or version changed, starting import (was: %s, now: %s)',
                        self._metadata.get('last-etag'),
                        response.headers['etag'])
            for chunk in response.iter_content(chunk_size=512):
                temp_file.write(chunk)
            self._metadata['last-etag'] = response.headers['etag']
            self._metadata['last-version'] = self._IMPORTER_VERSION
            return ZipFile(temp_file)
        else:
            LOGGER.info('No change to ETag or version, not importing files')

    def load(self):
        with TemporaryFile() as temp_file:
            cif_files = self._get_file_from_url(temp_file)
            if cif_files:
                self._schedule_service.reset(source='gmpte-cif')
                for cif_file in cif_files.namelist():
                    self._parser.import_file(cif_file[:-3], cif_files.open(cif_file))
