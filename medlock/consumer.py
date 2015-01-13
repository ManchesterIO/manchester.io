#!/srv/manchester.io/bin/medlock/bin/python

import logging
import os
from time import sleep

os.environ['CONFIG'] = '/srv/manchester.io/medlock.cfg'

from medlock.app import mq, app

console = logging.StreamHandler()
console.setFormatter(logging.Formatter('[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s'))
logging.getLogger().addHandler(console)
logging.getLogger('medlock').setLevel(logging.INFO)

mq.start()
mq.connect(username=app.config['NETWORK_RAIL_AUTH'][0],
           passcode=app.config['NETWORK_RAIL_AUTH'][1],
           wait=True)

mq.subscribe('/topic/VSTP_ALL', '{}-vstp'.format(app.config['NETWORK_RAIL_CONSUMER_ID']),
             ack='client-individual')

while mq.is_connected():
    sleep(1)
