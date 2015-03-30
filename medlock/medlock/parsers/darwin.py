import logging

LOGGER = logging.getLogger(__name__)


class DarwinPushPortParser(object):

    _XML_NAMESPACES = {
        'pp': '{http://www.thalesgroup.com/rtti/PushPort/v12}',
        'sched': '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}'
    }

    def parse(self, xml):
        messages = []
        for child in xml.find('./{pp}uR'.format(**self._XML_NAMESPACES)):
            if child.tag == '{pp}schedule'.format(**self._XML_NAMESPACES):
                if child.attrib.get('isPassengerSvc', 'true') == 'true':
                    messages.append(('activation', self._parse_schedule(child)))
            elif child.tag == '{pp}TS'.format(**self._XML_NAMESPACES):
                messages.append(('status', self._parse_status(child)))
            else:
                LOGGER.warning('Unexpected message type %s', child.tag)
        return messages

    def _parse_schedule(self, xml):
        activation_id = xml.attrib['rid']
        schedule = self._build_schedule(xml)
        return (activation_id, schedule)

    def _build_schedule(self, xml):
        return {
            'service_id': xml.attrib['uid'],
            'schedule_priority': 'P',
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
            return xml.attrib[key].replace(':', '')
        else:
            return None

    def _parse_status(self, xml):
        return None
