from datetime import timedelta
import logging
import requests
from tempfile import TemporaryFile
from zipfile import ZipFile

from celery.schedules import schedule

from medlock.parsers.naptan import NaptanParser

LOGGER = logging.getLogger(__name__)

class NaptanImporter(object):
    """
    Imports points of interest from the UK's National Public Transport Access Node dataset
    """

    IMPORT_SCHEDULE = schedule(run_every=timedelta(hours=6))

    NAPTAN_URL = "https://www.dft.gov.uk/NaPTAN/snapshot/NaPTANxml.zip"

    def __init__(self, location_service, metadata, interesting_areas):
        self._metadata = metadata
        self.parser = NaptanParser(location_service, interesting_areas)

    def _get_file_from_url(self, temp_file):
        response = requests.get(self.NAPTAN_URL, timeout=5, stream=True)

        if response.headers['etag'] != self._metadata.get('last-etag') or True:
            LOGGER.info('ETag changed, starting import (was: %s, now: %s)',
                        response.headers['etag'],
                        self._metadata.get('last-etag'))
            for chunk in response.iter_content():
                temp_file.write(chunk)
            xml_file = ZipFile(temp_file).open('NaPTAN.xml')
            self._metadata['last-etag'] = response.headers['etag']
            return xml_file
        else:
            LOGGER.info('No change to ETag, not importing files')

    def load(self):
        with TemporaryFile() as temp_file:
            naptan_file = self._get_file_from_url(temp_file)
            if naptan_file:
                self.parser.import_from_file(naptan_file)
