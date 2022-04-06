from functools import wraps, cached_property
from logging import getLogger
from uuid import uuid4

import django_rq
import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django.db import transaction, models
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.translation import gettext as _
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from rq import get_current_job

from worker.job_registry import get_job_types

logger = getLogger(__name__)
redis_cursor = redis.StrictRedis(host=settings.REDIS['HOST'], db=settings.REDIS['DB'])

status_choices = (
    ('queued', _('Sat i kø')),
    ('started', _('Igang')),
    ('deferred', _('Afventer')),
    ('failed', _('Fejlet')),
    ('finished', _('Færdig'))
)


class Job(models.Model):
    uuid = models.UUIDField(default=uuid4, blank=True, primary_key=True)
    pretty_title = models.CharField(max_length=255, blank=True, null=True)
    arguments = JSONField(default=dict)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    job_type = models.TextField(choices=((k, v['label'])for k, v in get_job_types().items()))
    rq_job_id = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('Job', null=True, blank=True, on_delete=models.CASCADE)
    checkpoint = JSONField(default=dict)
    progress = models.IntegerField(default=0, blank=True)
    status = models.TextField(default='queued', choices=status_choices, blank=True)
    traceback = models.TextField(default='', blank=True)
    queue = models.TextField(default='', blank=True)
    result = JSONField(default=dict)

    @property
    def has_running_subjobs(self):
        return self.job_set.exclude(status__in=['failed', 'finished']).exists()

    @property
    def bootstrap_color(self):
        if self.status == 'queued':
            return 'bg-warning'
        elif self.status == 'started' or self.has_running_subjobs:
            return 'bg-success'
        elif self.status == 'deferred':
            return 'bg-warning'
        elif self.status == 'failed':
            return 'bg-danger'
        elif self.status == 'finished':
            return 'bg-success'

    @property
    def bootstrap_progress_bar_class(self):
        classes = ['progress-bar', self.bootstrap_color]
        if self.status in ('queued', 'deferred'):
            classes.append('progress-bar-striped')
        elif self.status == 'started' or self.has_running_subjobs:
            classes.extend(('progress-bar-striped', 'progress-bar-animated'))
        return ' '.join(classes)

    @cached_property
    def job_type_dict(self):
        return get_job_types()[self.job_type]

    @cached_property
    def pretty_job_type(self):
        return self.job_type_dict['label']

    @property
    def pretty_job_title(self):
        return self.pretty_title or self.pretty_job_type

    @property
    def duration(self):
        if self.started_at is not None:
            if self.end_at is not None:
                return self.end_at - self.started_at
            else:
                return datetime.now() - self.started_at

    @property
    def all_completed(self):
        if self.status != 'finished':
            return False
        return not self.job_set.exclude(status='finished').exists()

    def get_rq_job(self):
        queue = django_rq.get_queue(self.queue, connection=redis_cursor)  # reuse same redis connection
        return queue.fetch_job(self.rq_job_id)

    @property
    def pretty_progress(self):
        return '{}%'.format(max(self.progress, 0))

    def set_progress(self, count, total, **kwargs):
        self.set_progress_pct((count / total) * 100, **kwargs)

    def set_progress_pct(self, progress, **kwargs):
        self.progress = progress
        self.save(update_fields=['progress'], **kwargs)

    @classmethod
    def schedule_job(cls, function, job_type, created_by, job_kwargs=None, queue='default', parent=None, depends_on=None):
        """
        :param function: function to execute
        :param created_by: Which user created the job.
        :param job_kwargs: kwargs to pass to the job
        :param job_type: used to indicate the job type
        :param queue: queue to schedule the function to
        :param parent the parent job that created this child job. Only used when spawning new jobs insides the job function.
        :param depends_on: Makes a job wait until the depending job is finished.
        result ttl no point in storing the result value in redis when we use this model to track state and we dont use
        result values.
        """
        if job_kwargs is None:
            job_kwargs = {}
        rq_queue = django_rq.get_queue(queue, connection=redis_cursor)  # reuse same redis connection
        job = cls.objects.create(job_type=job_type, created_by=created_by,
                                 parent=parent, arguments=job_kwargs, queue=queue)
        if depends_on:
            depends_on = depends_on.get_rq_job()
        rq_job = rq_queue.enqueue(function, result_ttl=0, depends_on=depends_on, meta={'job_uuid': job.uuid}, job_timeout=3600)

        job.rq_job_id = rq_job.get_id()
        job.statue = rq_job.get_status()
        job.save(update_fields=['rq_job_id', 'status'])

        return job

    def finish(self):
        """
        Mark a job as successfully completed.
        No reason to call this explicit when using the job_decorator.
        """
        if self.status == 'failed':
            # if the job is marked as failed just return instead of overwriting the the status
            return
        self.status = 'finished'
        self.progress = 100
        self.end_at = timezone.now()
        self.save(update_fields=['status', 'progress', 'end_at', 'result'])
        self.push_metrics()

    def push_metrics(self):
        """
        push a timestamp everytime a job is successfully executed
        """
        if settings.DEBUG is False and settings.METRICS['disable'] is False:
            # send metric to push gateway
            registry = CollectorRegistry()
            documentation = 'Last successful execution time for: %s' % self.get_job_type_display()
            g = Gauge('kas_job',
                      documentation,
                      registry=registry)
            g.set_to_current_time()
            try:
                push_to_gateway('pushgateway:9091', job=self.job_type, registry=registry)
            except Exception as e:
                # if pushing of metrics fail log it but dont mark the job as failed.
                logger.exception(e)

    def __str__(self):
        if self.parent:
            return '{} {}% (parent)'.format(self.status, self.progress)
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
        if job.status == 'started':
            job.finish()

    # make the original available to the pickle module as "<name>.original"
    inner.original = function
    inner.original.__qualname__ += ".original"

    return inner
