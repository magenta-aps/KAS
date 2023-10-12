# -*- coding: utf-8 -*-
import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from kas.models import PensionCompany

KAS_DIR = os.path.join(settings.BASE_DIR, "kas")
DATA_DIR = os.path.join(KAS_DIR, "data")

INPUT_FILE = os.path.join(DATA_DIR, "Pensionsudbydere i eSkat.csv")


class Command(BaseCommand):
    help = "Imports mockup data into the mockup tables for eSkat"

    companies_with_deals = (
        "55143315",  # PFA
        "34177104",  # PensionDanmark
    )

    def handle(self, *args, **kwargs):
        with open(INPUT_FILE) as csvfile:
            csvreader = csv.reader(csvfile)

            # Skip headers
            next(csvreader)

            for row in csvreader:
                res = row[0]
                if len(res) <= 4:
                    continue

                PensionCompany.objects.update_or_create(
                    defaults={
                        "res": res,
                        "name": row[1],
                        "address": row[2],
                        "agreement_present": (row[0] in self.companies_with_deals),
                    },
                    res=res,
                )
