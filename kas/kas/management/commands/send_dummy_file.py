import tempfile

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.datetime_safe import datetime

from tenQ.client import put_file_in_prisme_folder


class Command(BaseCommand):
    help = "Sends a dummy file to stating system"

    def add_arguments(self, parser):
        parser.add_argument("--filename", type=str, help="File name", default=None)
        parser.add_argument("--content", type=str, help="File contents", default=None)

    def handle(self, *args, **options):
        content = options.get("content") or "Dette er en test"
        destination_folder = settings.TENQ["dirs"]["10q_development"]
        filename = options.get("filename") or "Test_{}.txt".format(
            datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        )
        with tempfile.NamedTemporaryFile(mode="w") as batchfile:
            batchfile.write(content)
            batchfile.flush()
            put_file_in_prisme_folder(
                settings.TENQ, batchfile.name, destination_folder, filename, None
            )
        print("File uploaded")
