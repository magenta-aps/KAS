import os
import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils.autoreload import run_with_reloader


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("queues", nargs="+", type=str)
        parser.add_argument(
            "--worker-pid-file",
            action="store",
            dest="worker_pid_file",
            default="/tmp/rqworker.pid",
        )

    def handle(self, *args, **options):
        run_with_reloader(run_worker, options["queues"], options["worker_pid_file"])


def run_worker(queues, worker_pid_file):
    if os.path.exists(worker_pid_file):
        worker_pid = subprocess.run(
            ["cat", worker_pid_file], stdout=subprocess.PIPE
        ).stdout.decode("utf-8")
        kill_worker_cmd = f"kill {worker_pid}"
        subprocess.run(shlex.split(kill_worker_cmd), stderr=subprocess.PIPE)

    queues = " ".join(queues)
    start_worker_cmd = (
        f"{get_managepy_path()} rqworker {queues} --pid={worker_pid_file}"
    )
    subprocess.run(shlex.split(start_worker_cmd))


def get_managepy_path():
    managepy_path = None
    search_path = os.path.dirname(__file__)
    while not managepy_path:
        if os.path.exists(os.path.join(search_path, "manage.py")):
            managepy_path = os.path.abspath(os.path.join(search_path, "manage.py"))
        else:
            search_path = os.path.join(search_path, "../")
    return managepy_path
