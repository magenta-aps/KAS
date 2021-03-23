# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from eskat.models import MockModels
from eskat.mockupdata import import_default_mockup_data

import json
import os

ESKAT_DIR = os.path.join(settings.BASE_DIR, 'eskat')
DATA_DIR = os.path.join(ESKAT_DIR, 'data')

MANDTAL_FILE = os.path.join(DATA_DIR, 'kas_mandtal.json')
BEREGNINGER_X_FILE = os.path.join(DATA_DIR, 'kas_beregninger_x.json')
R75_FILE = os.path.join(DATA_DIR, 'r75_private_pension.json')


class Command(BaseCommand):
    help = 'Imports mockup data into the mockup tables for eSkat'

    def handle(self, *args, **kwargs):
        import_default_mockup_data()

    # Legacy method for importing from json files
    def import_mock_mandtal(self):

        model = MockModels.MockKasMandtal

        with open(MANDTAL_FILE) as io:
            json_data = json.load(io)
            for elem in json_data['data']:
                create_args = {k.lower(): v for k, v in elem.items()}
                try:
                    existing = model.objects.get(
                        pt_census_guid=create_args["pt_census_guid"]
                    )
                    for k, v in create_args.items():
                        setattr(existing, k, v)
                    existing.save()
                except model.DoesNotExist:
                    new_obj = model(**create_args)
                    new_obj.save()

    # Legacy method for importing from json files
    def import_mock_beregninger(self):

        model = MockModels.MockKasBeregningerX

        with open(BEREGNINGER_X_FILE) as io:
            json_data = json.load(io)

            for elem in json_data['data']:
                create_args = {k.lower(): v for k, v in elem.items()}

                # Populate each entry with data from mandtal
                mandtal = MockModels.MockKasMandtal.objects.get(
                    cpr=create_args['cpr'],
                    skatteaar=create_args['skatteaar'],
                )
                for k in (
                    'pt_census_guid',
                    'bank_reg_nr',
                    'bank_konto_nr',
                    'kommune_no',
                    'kommune',
                    'navn',
                    'adresselinje1',
                    'adresselinje2',
                    'adresselinje3',
                    'adresselinje4',
                    'adresselinje5',
                    'fuld_adresse',
                    'cpr_dashed',
                ):
                    create_args[k] = getattr(mandtal, k)

                try:
                    existing = model.objects.get(
                        pension_crt_calc_guid=create_args["pension_crt_calc_guid"]
                    )
                    for k, v in create_args.items():
                        setattr(existing, k, v)
                    existing.save()
                except model.DoesNotExist:
                    new_obj = model(**create_args)
                    new_obj.save()

    # Legacy method for importing from json files
    def import_mock_r75(self):
        # Method is not longer relevant and is not reimplemented for the
        # new R75 view.
        pass
