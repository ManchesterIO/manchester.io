#!/srv/manchester.io/bin/medlock/bin/python

from medlock.app import celery


celery.Worker().start()
