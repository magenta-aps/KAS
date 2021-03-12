# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from kas.models import PensionCompany

import csv
import os

KAS_DIR = os.path.join(settings.BASE_DIR, 'kas')
DATA_DIR = os.path.join(KAS_DIR, 'data')

INPUT_FILE = os.path.join(DATA_DIR, "Pensionsudbydere i eSkat.csv")


class Command(BaseCommand):
    help = 'Imports mockup data into the mockup tables for eSkat'

    def handle(self, *args, **kwargs):
        with open(INPUT_FILE) as csvfile:
            csvreader = csv.reader(csvfile)

            # Skip headers
            next(csvreader)

            for row in csvreader:
                dof = PensionCompany.DOF_UNKNOWN

                if row[3].lower() == "domestic":
                    dof = PensionCompany.DOF_DOMESTIC
                elif row[3].lower() == "foreign":
                    dof = PensionCompany.DOF_FOREIGN

                PensionCompany.objects.update_or_create(
                    defaults={
                        'res': row[0],
                        'name': row[1],
                        'address': row[2],
                        'domestic_or_foreign': dof,
                        'accepts_payments': True if row[4].lower() == "y" else False
                    },
                    res=row[0],
                )
