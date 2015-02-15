import logging
from xml.etree.cElementTree import iterparse

from geojson import GeoJSONEncoder
from shapely.geometry import Point


LOGGER = logging.getLogger(__name__)

NAPTAN_STOP_TYPES_TO_CATEGORIES = {
    'BCS': 'bus-stop',
    'BCT': 'bus-stop',
    'BCQ': 'bus-stop',
    'MET': {
        'MA': 'metrolink-station',
    },
    'PLT': None,
    'RLY': 'rail-station'
}


class NaptanParser(object):

    _STOP_POINT_ELEM = '{http://www.naptan.org.uk/}StopPoint'

    _STOP_TYPE_XPATH = './{http://www.naptan.org.uk/}StopClassification/{http://www.naptan.org.uk/}StopType'
    _ATCO_CODE_XPATH = './{http://www.naptan.org.uk/}AtcoCode'
    _CRS_CODE_XPATH = './{http://www.naptan.org.uk/}StopClassification/{http://www.naptan.org.uk/}OffStreet/' \
                      '{http://www.naptan.org.uk/}Rail/{http://www.naptan.org.uk/}AnnotatedRailRef/' \
                      '{http://www.naptan.org.uk/}CrsRef'
    _TIPLOC_XPATH = './{http://www.naptan.org.uk/}StopClassification/{http://www.naptan.org.uk/}OffStreet/' \
                    '{http://www.naptan.org.uk/}Rail/{http://www.naptan.org.uk/}AnnotatedRailRef/' \
                    '{http://www.naptan.org.uk/}TiplocRef'
    _NAPTAN_CODE_XPATH = './{http://www.naptan.org.uk/}NaptanCode'
    _LONGITUDE_XPATH = './{http://www.naptan.org.uk/}Place/{http://www.naptan.org.uk/}Location/' \
                         '{http://www.naptan.org.uk/}Translation/{http://www.naptan.org.uk/}Longitude'
    _LATITUDE_XPATH = './{http://www.naptan.org.uk/}Place/{http://www.naptan.org.uk/}Location/' \
                         '{http://www.naptan.org.uk/}Translation/{http://www.naptan.org.uk/}Latitude'
    _COMMON_NAME_XPATH = './{http://www.naptan.org.uk/}Descriptor/{http://www.naptan.org.uk/}CommonName'

    def __init__(self, location_service, interesting_codes):
        self._location_service = location_service
        self._interesting_codes = set(interesting_codes)

    def import_from_file(self, xml_file):
        self._seen_stops = set()
        self._stop_areas = dict()
        for event, elem in iterparse(xml_file, events=('end',)):
            if elem.tag == self._STOP_POINT_ELEM:
                category = self._get_category(
                    self._xpath(elem, self._STOP_TYPE_XPATH),
                    self._xpath(elem, self._ATCO_CODE_XPATH)
                )
                if category is not None:
                    identifier = self._get_identifier(category, elem)
                    self._process_stop(category, identifier, elem)

                elem.clear()

    def _get_identifier(self, category, elem):
        if category == 'rail-station':
            preferred_identifier = self._xpath(elem, self._CRS_CODE_XPATH)
        elif category == 'metrolink-station':
            preferred_identifier = self._xpath(elem, self._ATCO_CODE_XPATH)[8:11]
        elif category == 'bus-stop':
            preferred_identifier = self._xpath(elem, self._NAPTAN_CODE_XPATH)
        else:
            LOGGER.warning('Getting identifier for an unknown type %s', category)
            preferred_identifier = None

        if preferred_identifier:
            return preferred_identifier
        else:
            return self._xpath(elem, self._ATCO_CODE_XPATH)

    def _get_category(self, stop_type, atco_code):
        if atco_code[:3] not in self._interesting_codes:
            return None
        elif stop_type in ['MET', 'PLT']:
            subtype = atco_code[6:8]
            if subtype in self._interesting_codes:
                return NAPTAN_STOP_TYPES_TO_CATEGORIES['MET'].get(subtype)
            else:
                return None
        else:
            return NAPTAN_STOP_TYPES_TO_CATEGORIES.get(stop_type)

    def _process_stop(self, category, identifier, elem):
        if (category, identifier) not in self._seen_stops:
            if elem.attrib['Status'] != 'active':
                LOGGER.info("Deleting %s %s a status is %s", category, identifier, elem.attrib['Status'])
                self._location_service.delete(category, identifier)
            else:
                LOGGER.info("Updating %s %s", category, identifier)
                self._location_service.update(
                    stop_type=category,
                    identifier=identifier,
                    name=self._get_name(category, elem),
                    location=GeoJSONEncoder().default(self._get_location(elem)),
                )
                self._seen_stops.add((category, identifier))

        if elem.attrib['Status'] == 'active':
            self._location_service.add_additional_identifier(
                category, identifier, **self._get_additional_identifiers(elem))

    def _get_name(self, category, elem):
        namer = {
            'bus-stop': self._common_name(),
            'rail-station': self._common_name(strip=' Rail Station'),
            'metrolink-station': self._common_name(strip=' (Manchester Metrolink)')
        }.get(category)
        if namer is None:
            LOGGER.warn('Attemping to name %s which is an unknown category %s',
                        self._xpath(elem, self._ATCO_CODE_XPATH),
                        category)
            namer = self._common_name()
        return namer(elem)

    def _common_name(self, strip=None):
        def namer(elem):
            common_name = self._xpath(elem, self._COMMON_NAME_XPATH)
            if strip is not None:
                return common_name.split(strip)[0]
            else:
                return common_name
        return namer

    def _get_location(self, elem):
        return Point(
            float(self._xpath(elem, self._LONGITUDE_XPATH)),
            float(self._xpath(elem, self._LATITUDE_XPATH))
        )

    def _get_additional_identifiers(self, elem):
        atco_code = self._xpath(elem, self._ATCO_CODE_XPATH)
        additional_identifiers = {
            'atco': atco_code
        }
        tiploc = self._xpath(elem, self._TIPLOC_XPATH)
        if tiploc:
            additional_identifiers['tiploc'] = tiploc
        elif atco_code.startswith('9100'):
            additional_identifiers['tiploc'] = atco_code[4:]
        return additional_identifiers

    def _xpath(self, elem, xpath):
        node = elem.find(xpath)
        if node is not None:
            return node.text
        else:
            return None
