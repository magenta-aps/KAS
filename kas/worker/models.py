import django_rq
from django.db import transaction, models
from rq import get_current_job
from functools import wraps
import redis
from uuid import uuid4
from django.utils import timezone
from django.conf import settings
redis_cursor = redis.StrictRedis(host=settings.REDIS['HOST'], db=settings.REDIS['DB'])

status_choices = (
    ('queued', 'Pending'),
    ('started', 'Started'),
    ('deferred', 'Deferred'),
    ('failed', 'Failed'),
    ('finished', 'Finished')
)

job_types = (
    ('slow_job', 'Slow job'),
    ('slow_job_with_children', 'Job with children'),
    ('job_with_exception', 'Job with exception')
)


class Job(models.Model):
    uuid = models.UUIDField(default=uuid4, blank=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    job_type = models.TextField(choices=job_types)
    rq_job_id = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('Job', null=True, blank=True, on_delete=models.CASCADE)
    checkpoint = models.TextField(default='', blank=True)
    progress = models.IntegerField(default=0, blank=True)
    status = models.TextField(default='queued', choices=status_choices, blank=True)
    traceback = models.TextField(default='', blank=True)


    @property
    def bootstrap_color(self):
        if self.status == 'queued':
            return 'progress-bar bg-warning progress-bar-striped'
        elif self.status == 'started' or self.job_set.exclude(status__in=['failed', 'finished']).exists():
            return 'progress-bar bg-success progress-bar-striped progress-bar-animated'
        elif self.status == 'deferred':
            return 'progress-bar progress-bar-striped bg-warning'
        elif self.status == 'failed':
            return 'progress-bar bg-danger'
        elif self.status == 'finished':
            return 'progress-bar bg-success'

    @property
    def title(self):
        return self.job_type.replace('_', ' ').capitalize()

    @property
    def all_completed(self):
        if self.status != 'finished':
            return False
        return not self.job_set.exclude(status='finished').exists()

    @property
    def pretty_progress(self):
        return '{}%'.format(max(self.progress, 1))

    def set_progress(self, count, total):
        self.progress = (count / total) * 100
        self.save(update_fields=['progress'])

    def to_dict(self):
        return {'id': self.pk,
                'title': self.title,
                'progress': self.pretty_progress,
                'status': self.status,
                'completed': self.all_completed,
                'classes': self.bootstrap_color,
                'jobs': [child.to_dict() for child in self.job_set.all()]}

    @classmethod
    def schedule_job(cls, job_type, f, args=(), kwargs=None, queue='default', parent=None):
        """
        :param f: function to execute
        :param args: args to call the function with
        :param kwargs:
        :param job_type: used to indicate the job type
        :param queue: queue to schedule the function to
        :param parent
        result ttl no point in storing the result value in redis when we use this model to track state and we dont use
        result values.
        """
        queue = django_rq.get_queue(queue, connection=redis_cursor)  # reuse same redis connection
        job = cls.objects.create(job_type=job_type, parent=parent)
        rq_job = queue.enqueue(f, args=args, kwargs=kwargs, result_ttl=0, meta={'job_uuid': job.uuid})
        job.rq_job_id = rq_job.get_id()
        job.statue = rq_job.get_status()
        job.save(update_fields=['rq_job_id', 'status'])
        return job

    def __str__(self):
        return '{} {}%'.format(self.status, self.progress)

    class Meta:
        ordering = ('-created_at', )


def job_decorator(function):
    @wraps(function)
    def inner():
        rq_job = get_current_job()
        with transaction.atomic():
            job = Job.objects.select_for_update().filter(uuid=rq_job.meta['job_uuid'])[0]
            job.status = rq_job.get_status()
            job.progress = 0
            job.started_at = timezone.now()
            job.save(update_fields=['status', 'progress', 'started_at'])

        function(job)
        job.status = 'finished'
        job.progress = 100
        job.end_at = timezone.now()
        job.save(update_fields=['status', 'progress', 'end_at'])

    # make the original available to the pickle module as "<name>.original"
    inner.original = function
    inner.original.__qualname__ += ".original"

    return inner
