import celery
import celery.beat


class Celery(celery.Celery):

    def __init__(self, app):
        super(Celery, self).__init__(__package__, loader='default')
        self.config_from_object(app.config)
        self.periodic_tasks = {}

    def periodic_task(self, *args, **kwargs):
        crontab = kwargs.pop('crontab')
        task = self.task(*args, **kwargs)
        self.periodic_tasks[task.name] = {'task': task, 'schedule': crontab}
        return task


class Scheduler(celery.beat.PersistentScheduler):

    def setup_schedule(self):
        super(Scheduler, self).setup_schedule()
        self.merge_inplace(self.app.periodic_tasks)
