from datetime import datetime
import logging

LOGGER = logging.getLogger(__name__)

class CifParser(object):

    def __init__(self, schedule_service):
        self._schedule_service = schedule_service

    def import_file(self, service_key, cif_file):
        for schedule in self._parse_file(cif_file):
            LOGGER.info("Inserting schedule {service_key}{schedule_id}".format(service_key=service_key,
                                                                               schedule_id=schedule['identifier']))
            self._schedule_service.insert(source='gmpte-cif', **self._build_schedule(service_key, schedule))

    def _parse_file(self, cif_file):
        in_journey = False
        current_journey_lines = []
        for line_no, line in enumerate(cif_file):
            if line.startswith('QS'):
                in_journey = True
                current_journey_lines = []
            if in_journey:
                current_journey_lines.append(line)
            elif line[:2] not in ['AT', 'ZL', 'ZD', 'ZS', 'ZA']:
                LOGGER.info('Ignoring non-journey line with header: {header}'.format(header=line[:2]))
            if line.startswith('QT'):
                in_journey = False
                journey = self._parse_journey(line_no, current_journey_lines)
                if journey:
                    yield journey

    def _parse_journey(self, journey_id, journey_lines):
        journey = {
            'identifier': None,
            'schedule_start': None,
            'schedule_end': None,
            'calling_points': [],
            'activate_on': {
                'monday': False,
                'tuesday': False,
                'wednesday': False,
                'thursday': False,
                'friday': False,
                'saturday': False,
                'sunday': False,
                'bank-holidays': None,
                'school-holidays': None
            }
        }

        for line in journey_lines:
            if line.startswith('QS'):
                journey['identifier'] = str(journey_id)
                journey['schedule_start'] = line[13:21]
                journey['schedule_end'] = line[21:29]
                journey['activate_on']['monday'] = line[29]
                journey['activate_on']['tuesday'] = line[30]
                journey['activate_on']['wednesday'] = line[31]
                journey['activate_on']['thursday'] = line[32]
                journey['activate_on']['friday'] = line[33]
                journey['activate_on']['saturday'] = line[34]
                journey['activate_on']['sunday'] = line[35]
                journey['activate_on']['school-holidays'] = line[36]
                journey['activate_on']['bank-holidays'] = line[37]
                journey['public_id'] = line[38:42]
                journey['vehicle_type'] = line[48:56]
            elif line.startswith('QO'):
                journey['calling_points'].append({
                    'atco': line[2:14],
                    'arrival': None,
                    'departure': line[14:18],
                    'pass': False
                })
            elif line.startswith('QI'):
                journey['calling_points'].append({
                    'atco': line[2:14],
                    'arrival': line[14:18],
                    'departure': line[18:22],
                    'pass': line[22] == 'N'
                })
            elif line.startswith('QT'):
                journey['calling_points'].append({
                    'atco': line[2:14],
                    'arrival': line[14:18],
                    'departure': None,
                    'pass': False
                })
            elif line[:2] not in ['ZJ', 'ZN']:
                LOGGER.info('Ignoring journey line with header: {header}'.format(header=line[:2]))

        return journey

    def _build_schedule(self, service_key, schedule):
        return {
            'service_id': service_key + schedule['identifier'].strip(),
            'service_type': {'METRO': 'metrolink', 'BUS': 'bus'}[schedule['vehicle_type'].strip()],
            'public_id': schedule['public_id'].strip(),
            'schedule_priority': 'P',
            'schedule_start': datetime.strptime(schedule['schedule_start'], '%Y%m%d').strftime('%Y-%m-%d'),
            'schedule_expires': datetime.strptime(schedule['schedule_end'], '%Y%m%d').strftime('%Y-%m-%d'),
            'calling_points': map(self._build_calling_point, schedule['calling_points']),
            'activate_on': {
                'monday': schedule['activate_on']['monday'] == '1',
                'tuesday': schedule['activate_on']['tuesday'] == '1',
                'wednesday': schedule['activate_on']['wednesday'] == '1',
                'thursday': schedule['activate_on']['thursday'] == '1',
                'friday': schedule['activate_on']['friday'] == '1',
                'saturday': schedule['activate_on']['saturday'] == '1',
                'sunday': schedule['activate_on']['sunday'] == '1',
                'bank-holidays': {'X': False, 'A': 'always', 'B': True, ' ': None}[schedule['activate_on']['bank-holidays']],
                'school-holidays': {'S': False, 'H': True, '1': True, ' ': None, '0': None}[schedule['activate_on']['school-holidays']],
            }
        }

    def _build_calling_point(self, calling_point):
        arrival = calling_point['arrival'] + '00' if calling_point['arrival'] else None
        departure = calling_point['departure'] + '00' if calling_point['departure'] else None

        return {
            'atco': calling_point['atco'].strip(),
            'platform': None,
            'public_arrival': arrival if not calling_point['pass'] else None,
            'public_departure': departure if not calling_point['pass'] else None,
            'arrival': arrival,
            'departure': departure
        }
