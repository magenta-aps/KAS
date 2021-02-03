from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.utils import OperationalError
from psycopg2 import OperationalError as PsycopgOpError
from time import sleep


class Command(BaseCommand):
    help = 'reverse geocode positions'

    def handle(self, *args, **options):
        while True:
            try:
                conn = connections['default']
            except (OperationalError, PsycopgOpError) as e:
                print('waiting for database to come online!')
                sleep(1)
            else:
                conn.close()
                print('database online')
                break
