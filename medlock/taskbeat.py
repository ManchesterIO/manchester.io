#!/srv/manchester.io/bin/medlock/bin/python

from medlock.app import celery
from medlock.scheduler import Scheduler

beat = celery.Beat()
beat.scheduler_cls = Scheduler
beat.run()
