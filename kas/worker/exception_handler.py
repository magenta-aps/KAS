from django.db.transaction import atomic
from django.utils import timezone
from worker.models import Job
import traceback


def write_exception_to_db(rq_job, exc_type, exc_value, tb):
    # do custom things here
    # for example, write the exception info to a DB
    job_uuid = rq_job.meta.get('job_uuid', None)
    if job_uuid:
        # we cant get the related job model instance
        with atomic():
            job = Job.objects.select_for_update().filter(uuid=job_uuid)[0]
            job.traceback = repr(traceback.format_exception(exc_type, exc_value, tb))
            job.status = 'failed'
            job.end_at = timezone.now()
            job.save(update_fields=['status', 'traceback', 'end_at'])
            # SEND stuff to sentry?
            return False
    return True
