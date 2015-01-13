import celery
import celery.beat


class Celery(celery.Celery):

    def __init__(self, app):
        super(Celery, self).__init__()
        self.config_from_object(app.config)
        self.periodic_tasks = {}

    def task(self, *args, **kwargs):
        crontab = kwargs.pop('crontab', None)
        task = super(Celery, self).task(*args, **kwargs)
        if crontab:
            self.periodic_tasks[task.name] = {'task': task.name, 'schedule': crontab}
        return task


class Scheduler(celery.beat.PersistentScheduler):

    def setup_schedule(self):
        super(Scheduler, self).setup_schedule()
        self.merge_inplace(self.app.periodic_tasks)
