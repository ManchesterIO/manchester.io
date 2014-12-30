import logging
from xml.etree.cElementTree import iterparse

from shapely.geometry import Point


LOGGER = logging.getLogger(__name__)

NAPTAN_STOP_TYPES_TO_CATEGORIES = {
    'BCS': 'bus-stop',
    'BCT': 'bus-stop',
    'BCQ': 'bus-stop',
    'MET': {
        'AL': 'air-line',
        'BP': 'tramway-stop',
        'CR': 'tramlink-stop',
        'DL': 'dlr-station',
        'GL': 'subway-station',
        'GW': 'gatwick-shuttle-station',
        'LU': 'tube-station',
        'MA': 'metrolink-station',
        'NO': 'net-stop',
        'SY': 'supertram-stop',
        'WM': 'midland-metro-stop',
    },
    'RLY': 'rail-station'
}


class NaptanParser(object):

    _ROOT_ELEM = '{http://www.naptan.org.uk/}NaPTAN'
    _STOP_POINT_ELEM = '{http://www.naptan.org.uk/}StopPoint'

    _STOP_TYPE_XPATH = './{http://www.naptan.org.uk/}StopClassification/{http://www.naptan.org.uk/}StopType'
    _ATCO_CODE_XPATH = './{http://www.naptan.org.uk/}AtcoCode'
    _CRS_CODE_XPATH = './{http://www.naptan.org.uk/}StopClassification/{http://www.naptan.org.uk/}OffStreet/' \
                      '{http://www.naptan.org.uk/}Rail/{http://www.naptan.org.uk/}AnnotatedRailRef/' \
                      '{http://www.naptan.org.uk/}CrsRef'
    _TIPLOC_CODE_XPATH = './{http://www.naptan.org.uk/}StopClassification/{http://www.naptan.org.uk/}OffStreet/' \
                         '{http://www.naptan.org.uk/}Rail/{http://www.naptan.org.uk/}AnnotatedRailRef/' \
                         '{http://www.naptan.org.uk/}TiplocRef'
    _LONGITUDE_XPATH = './{http://www.naptan.org.uk/}Place/{http://www.naptan.org.uk/}Location/' \
                         '{http://www.naptan.org.uk/}Translation/{http://www.naptan.org.uk/}Longitude'
    _LATITUDE_XPATH = './{http://www.naptan.org.uk/}Place/{http://www.naptan.org.uk/}Location/' \
                         '{http://www.naptan.org.uk/}Translation/{http://www.naptan.org.uk/}Latitude'

    def __init__(self, location_service, interesting_codes):
        self._interesting_codes = set(interesting_codes)

    def import_from_file(self, xml_file):
        for event, elem in iterparse(xml_file, events=('end',)):
            if elem.tag == self._STOP_POINT_ELEM:
                atco_code = self._xpath(elem, self._ATCO_CODE_XPATH)
                stop_type = self._xpath(elem, self._STOP_TYPE_XPATH)
                category = self._get_category(stop_type, atco_code)
                if category is not None:
                     LOGGER.info("Importing %s as %s", atco_code, category)

                elem.clear()

    def _get_category(self, stop_type, atco_code):
        if atco_code[:3] not in self._interesting_codes:
            return None
        elif stop_type == 'MET':
            subtype = atco_code[6:8]
            if subtype in self._interesting_codes:
                return NAPTAN_STOP_TYPES_TO_CATEGORIES[stop_type].get(subtype)
            else:
                return None
        else:
            return NAPTAN_STOP_TYPES_TO_CATEGORIES.get(stop_type)

    def _xpath(self, elem, xpath):
        return elem.find(xpath).text
