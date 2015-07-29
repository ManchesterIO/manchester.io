from datetime import date, datetime
import logging
from xml.etree.ElementTree import tostring

from medlock.services.schedules import ScheduleService

LOGGER = logging.getLogger(__name__)


class DarwinPushPortParser(object):

    _XML_NAMESPACES = {
        'pp': '{http://www.thalesgroup.com/rtti/PushPort/v12}',
        'sched': '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}',
        'forecast': '{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}'
    }

    def __init__(self, statsd):
        self._statsd = statsd

    def parse(self, xml):
        messages = []
        for child in xml.find('./{pp}uR'.format(**self._XML_NAMESPACES)):
            if child.tag == '{pp}schedule'.format(**self._XML_NAMESPACES):
                self._statsd.incr(__name__ + '.schedule')
                if child.attrib.get('isPassengerSvc', 'true') == 'true':
                    messages.append(('activation', self._parse_schedule(child)))
            elif child.tag == '{pp}TS'.format(**self._XML_NAMESPACES):
                self._statsd.incr(__name__ + '.train_status')
                messages.append(('status', self._parse_status(child)))
            elif child.tag == '{pp}association'.format(**self._XML_NAMESPACES):
                self._statsd.incr(__name__ + '.association')
                messages.append(('association', self._parse_association(child)))
            elif child.tag == '{pp}deactivated'.format(**self._XML_NAMESPACES):
                self._statsd.incr(__name__ + '.deactivation')
                messages.append(('deactivation', self._parse_deactivated(child)))
            else:
                self._statsd.incr(__name__ + '.unknown')
                LOGGER.warning('Unexpected message type %s', child.tag)
                LOGGER.info(tostring(child))
        return messages

    def _parse_schedule(self, xml):
        activation_id = xml.attrib['rid']
        schedule = self._build_schedule(xml)
        return (activation_id, schedule)

    def _build_schedule(self, xml):
        return {
            'source': 'darwin',
            'service_id': xml.attrib['uid'],
            'schedule_start': xml.attrib['ssd'],
            'schedule_expires': xml.attrib['ssd'],
            'calling_points': [
                self._build_calling_point(xml.find('{sched}OR'.format(**self._XML_NAMESPACES)))
            ] + map(self._build_calling_point, xml.findall('{sched}IP'.format(**self._XML_NAMESPACES))) + [
                self._build_calling_point(xml.find('{sched}DT'.format(**self._XML_NAMESPACES)))
            ]
        }

    def _build_calling_point(self, xml):
        return {
            'tiploc': xml.attrib['tpl'],
            'platform': None,
            'public_arrival': self._get_time_attribute(xml, 'pta'),
            'public_departure': self._get_time_attribute(xml, 'ptd'),
            'arrival': self._get_time_attribute(xml, 'wta'),
            'departure': self._get_time_attribute(xml, 'wtd')
        }

    def _get_time_attribute(self, xml, key):
        if key in xml.attrib:
            return self._convert_timestamp(xml.attrib[key]).strftime('%H%M%S')
        else:
            return None

    def _convert_timestamp(self, timestamp):
        if len(timestamp) == 5:
            timestamp += ':00'
        return datetime.strptime(timestamp, '%H:%M:%S').time()


    def _parse_status(self, xml):
        updates = []
        for location in xml.findall('{forecast}Location'.format(**self._XML_NAMESPACES)):
            expected_arrival = location.attrib.get('wta', None)
            expected_departure = location.attrib.get('wtd', None)
            for arrival in location.findall('{forecast}arr'.format(**self._XML_NAMESPACES)):
                if 'at' in arrival.attrib:
                    updates.append((self._convert_to_datetime(expected_arrival),
                                    ScheduleService.ARRIVAL_EVENT,
                                    self._convert_to_datetime(arrival.attrib['at']),
                                    ScheduleService.ACTUAL))
                if 'et' in arrival.attrib:
                    updates.append((self._convert_to_datetime(expected_arrival),
                                    ScheduleService.ARRIVAL_EVENT,
                                    self._convert_to_datetime(arrival.attrib['et']),
                                    ScheduleService.PREDICTED))
            for departure in location.findall('{forecast}dep'.format(**self._XML_NAMESPACES)):
                if 'at' in departure.attrib:
                    updates.append((self._convert_to_datetime(expected_departure),
                                    ScheduleService.DEPARTURE_EVENT,
                                    self._convert_to_datetime(departure.attrib['at']),
                                    ScheduleService.ACTUAL))
                if 'et' in departure.attrib:
                    updates.append((self._convert_to_datetime(expected_departure),
                                    ScheduleService.DEPARTURE_EVENT,
                                    self._convert_to_datetime(departure.attrib['et']),
                                    ScheduleService.PREDICTED))
        return (xml.attrib['rid'], updates)

    def _convert_to_datetime(self, timestamp):
        # TODO: This logic will break after midnight!!
        return datetime.combine(date.today(), self._convert_timestamp(timestamp))

    def _parse_association(self, xml):
        return None

    def _parse_deactivated(self, xml):
        return xml.attrib['rid']
