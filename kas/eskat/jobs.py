from eskat.mockupdata import import_default_mockup_data
from worker.models import job_decorator


@job_decorator
def import_eskat_mockup(job):
    try:
        import_default_mockup_data()
        status = "OK"
        message = ""
    except Exception as e:
        status = "Fejl",
        message = str(e)

    job.result = {
        "status": status,
        "message": message,
    }

    job.set_progress_pct(100)
