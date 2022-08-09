from django.core.management.base import BaseCommand, CommandError
from worker.job_registry import get_job_types, resolve_job_function
from worker.models import Job
from django.contrib.auth import get_user_model
from django.utils import timezone


class Command(BaseCommand):
    help = "Run a job periodically with pre-defined arguments"

    def add_arguments(self, parser):
        parser.add_argument("job_type", type=str)

    def handle(self, *args, **options):
        try:
            job_type = get_job_types()[options["job_type"]]
        except KeyError:
            raise CommandError("No such job type %s" % (options["job_type"]))
        # ensure the scheduler user exists
        user, _ = get_user_model().objects.get_or_create(
            username="scheduler", defaults={"is_active": False}
        )
        job_kwargs = {}
        if options["job_type"] == "ImportMandtalJob":
            # set current year as job argument
            job_kwargs.update({"year": timezone.now().year})

        Job.schedule_job(
            resolve_job_function(job_type["function"]),
            job_type=options["job_type"],
            created_by=user,
            job_kwargs=job_kwargs,
        )
