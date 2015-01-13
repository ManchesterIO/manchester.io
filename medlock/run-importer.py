#!/srv/manchester.io/bin/medlock/bin/python

import logging
import os
import sys

os.environ['CONFIG'] = '/srv/manchester.io/medlock.cfg'

from medlock.app import app, import_naptan, import_network_rail_schedule

console = logging.StreamHandler()
console.setFormatter(logging.Formatter('[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s'))
logging.getLogger().addHandler(console)
logging.getLogger('medlock').setLevel(logging.INFO)

IMPORTERS = {
    'naptan': import_naptan,
    'nrod-schedule': import_network_rail_schedule
}

if len(sys.argv) != 2 or not IMPORTERS.has_key(sys.argv[1]):
    print "Usage: {command} <importer>".format(command=sys.argv[0])
    print ""
    print "Valid importers:"
    for importer_name in IMPORTERS.keys():
        print "    {importer}".format(importer=importer_name)
    print

else:

    with app.app_context():
        IMPORTERS[sys.argv[1]]()
