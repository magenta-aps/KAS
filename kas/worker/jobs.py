from worker.models import job_decorator, Job
from time import sleep


@job_decorator
def slow_job(job):
    for i in range(1, 10):
        job.progress = 10*i
        job.save(update_fields=['progress'])
        sleep(10)


@job_decorator
def slow_job_with_children(job):
    Job.schedule_job('slow_job', slow_job, parent=job)
    for i in range(1, 10):
        job.progress = 10*i
        job.save(update_fields=['progress'])
        sleep(1)
    Job.schedule_job('slow_job', slow_job, parent=job)


@job_decorator
def job_with_exception(job):
    job.progress = 20
    job.save(update_fields=['progress'])
    a = 1/0 # noqa
