#!/srv/manchester.io/bin/medlock/bin/python

import logging
import sys

from medlock.app import app, naptan_importer

console = logging.StreamHandler()
console.setFormatter(logging.Formatter('[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s'))
logging.getLogger().addHandler(console)
logging.getLogger('medlock').setLevel(logging.INFO)

IMPORTERS = {
    'naptan': naptan_importer
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
        IMPORTERS[sys.argv[1]].load()
