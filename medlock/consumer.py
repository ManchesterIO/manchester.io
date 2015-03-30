#!/srv/manchester.io/bin/medlock/bin/python

import logging
import os
from time import sleep

os.environ['CONFIG'] = '/srv/manchester.io/medlock.cfg'

from medlock.app import mq, app

if app.debug:
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s'))
    logging.getLogger().addHandler(console)
    logging.getLogger('medlock').setLevel(logging.INFO)

mq.start()
mq.connect(username='d3user',
           passcode='d3password',
           wait=True)

mq.subscribe(app.config['NATIONAL_RAIL_QUEUE_NAME'], app.config['NATIONAL_RAIL_CONSUMER_ID'],
             ack='client-individual')

while mq.is_connected():
    sleep(1)
