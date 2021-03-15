from django.db import transaction
from django.utils import timezone
from eskat.models import ImportedKasMandtal, ImportedR75PrivatePension
from eskat.models import get_kas_mandtal_model, get_r75_private_pension_model
from kas.models import Person, PersonTaxYear, TaxYear, PolicyTaxYear, PensionCompany, TaxSlipGenerated
from kas.eboks import EboksClient, EboksDispatchGenerator
from kas.reportgeneration.kas_report import TaxPDF
from requests.exceptions import HTTPError, ConnectionError
from rq import get_current_job
from time import sleep
from worker.models import job_decorator, Job

import base64
import traceback


@job_decorator
def import_mandtal(job):
    year = job.arguments['year']
    tax_year = TaxYear.objects.get(year=year)
    number_of_progress_segments = 2
    progress_factor = 1 / number_of_progress_segments
    mandtal_created, mandtal_updated = ImportedKasMandtal.import_year(year, job, progress_factor, 0)

    qs = get_kas_mandtal_model().objects.filter(skatteaar=year)
    count = qs.count()
    progress_start = 0.5
    (persons_created, persons_updated) = (0, 0)
    (persontaxyears_created, persontaxyears_updated) = (0, 0)

    for i, item in enumerate(qs.iterator()):

        person_data = {
            'cpr': item.cpr,
            'municipality_name': item.kommune,
            'municipality_code': item.kommune_no,
            'address_line_1': item.adresselinje1,
            'address_line_2': item.adresselinje2,
            'address_line_3': item.adresselinje3,
            'address_line_4': item.adresselinje4,
            'address_line_5': item.adresselinje5,
            'full_address': item.fuld_adresse,
        }

        (person, status) = Person.update_or_create(person_data, 'cpr')
        if status == Person.CREATED:
            persons_created += 1
        elif status == Person.UPDATED:
            persons_updated += 1

        person_tax_year_data = {
            'person': person,
            'tax_year': tax_year,
            'number_of_days': item.skattedage,
            'fully_tax_liable': item.skatteomfang is not None and item.skatteomfang.lower() == 'fuld skattepligtig',
        }

        (person_tax_year, status) = PersonTaxYear.update_or_create(person_tax_year_data, 'tax_year', 'person')
        if status == PersonTaxYear.CREATED:
            persontaxyears_created += 1
        elif status == PersonTaxYear.UPDATED:
            persontaxyears_updated += 1

        job.set_progress_pct(progress_start + (i / count) * (100 * progress_factor))

    job.result = {'summary': [
        {'label': 'Rå Mandtal-objekter', 'value': [
            {'label': 'Tilføjet', 'value': mandtal_created},
            {'label': 'Opdateret', 'value': mandtal_updated}
        ]},
        {'label': 'Person-objekter', 'value': [
            {'label': 'Tilføjet', 'value': persons_created},
            {'label': 'Opdateret', 'value': persons_updated}
        ]},
        {'label': 'Personskatteår-objekter', 'value': [
            {'label': 'Tilføjet', 'value': persontaxyears_created},
            {'label': 'Opdateret', 'value': persontaxyears_updated}
        ]}
    ]}

@job_decorator
def import_r75(job):
    year = job.arguments['year']
    tax_year = TaxYear.objects.get(year=year)
    number_of_progress_segments = 2
    progress_factor = 1 / number_of_progress_segments
    (r75_created, r75_updated) = ImportedR75PrivatePension.import_year(year, job, progress_factor, 0)

    progress_start = 0.5
    persons_created = 0
    person_tax_years_created = 0
    (policies_created, policies_updated) = (0, 0)

    qs = get_r75_private_pension_model().objects.filter(tax_year=year)
    count = qs.count()
    for i, item in enumerate(qs):

        person, c = Person.objects.get_or_create(cpr=item.cpr)
        if c:
            persons_created += 1
        person_tax_year, c = PersonTaxYear.objects.get_or_create(person=person, tax_year=tax_year)
        if c:
            person_tax_years_created += 1

        res = int(item.res)
        pension_company, c = PensionCompany.objects.get_or_create(**{'res': res})

        policy_data = {
            'person_tax_year': person_tax_year,
            'pension_company': pension_company,
            'policy_number': item.pkt,
            'prefilled_amount': item.beloeb,
        }
        (policy_tax_year, status) = PolicyTaxYear.update_or_create(policy_data, 'person_tax_year', 'pension_company', 'policy_number')

        if status in (PersonTaxYear.CREATED, PersonTaxYear.UPDATED):
            policy_tax_year.recalculate()
            if status == PersonTaxYear.CREATED:
                policies_created += 1
            elif status == PersonTaxYear.UPDATED:
                policies_updated += 1

        job.set_progress_pct(progress_start + (i / count) * (100 * progress_factor))

    job.result = {'summary': [
        {'label': 'Rå R75-objekter', 'value': [
            {'label': 'Tilføjet', 'value': r75_created},
            {'label': 'Opdateret', 'value': r75_updated}
        ]},
        {'label': 'Policeskatteår-objekter', 'value': [
            {'label': 'Tilføjet', 'value': policies_created},
            {'label': 'Opdateret', 'value': policies_updated}
        ]}
    ]}

def chunks(lst, size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def update_status_for_pending_dispatches(eboks_client, pending_messages):
    for message_id_chunk in chunks(list(pending_messages.keys()), size=50):
        # Send up to 50 message_ids to get status information for
        r = eboks_client.get_recipient_status(message_id_chunk)
        for message in r.json():
            # we only use 1 recipient
            recipient = message['recipients'][0]
            if message['message_id'] in pending_messages and recipient['post_processing_status'] != 'pending':
                # if state change update it
                slip = pending_messages[message['message_id']]
                slip.post_processing_status = recipient['post_processing_status']
                if recipient['post_processing_status'] in ('address resolved', 'remote printed'):
                    # mark the message as sent when post processing is done
                    slip.status = 'sent'
                elif recipient['post_processing_status'] == 'address not found':
                    # if we could not find an address mark it as failed.
                    slip.status = 'failed'
                slip.save()


def dispatch_tax_year():
    rq_job = get_current_job()
    with transaction.atomic():
        job = Job.objects.select_for_update().filter(uuid=rq_job.meta['job_uuid'])[0]
        job.status = rq_job.get_status()
        job.progress = 0
        job.started_at = timezone.now()
        total = TaxSlipGenerated.objects.filter(status='created').\
            filter(persontaxyear__tax_year__pk=job.arguments['year_pk']).count()
        job.arguments['total_count'] = total
        job.arguments['current_count'] = 0
        job.save(update_fields=['status', 'progress', 'started_at', 'arguments'])

    if job.arguments['total_count'] > 0:
        Job.schedule_job(dispatch_eboks_tax_slips, 'dispatch_tax_year_child', job.created_by, parent=job)
    else:
        job.finish()


def mark_parent_job_as_failed(child_job, progress=None):
    parent = child_job.parent
    parent.status = child_job.status
    parent.result = child_job.result
    update_fields = ['status', 'result']
    if progress:
        parent.progress = progress
        update_fields.append('progress')
    parent.save(update_fields=update_fields)


@job_decorator
def dispatch_eboks_tax_slips(job):
    from django.conf import settings
    dispatch_page_size = settings.EBOKS['dispatch_bulk_size']
    title = job.parent.arguments['title']
    generator = EboksDispatchGenerator.from_settings(title=title)
    client = EboksClient.from_settings()
    i = 1
    has_more = False
    slips = TaxSlipGenerated.objects.filter(status='created').filter(
        persontaxyear__tax_year__pk=job.parent.arguments['year_pk']).select_for_update(skip_locked=True)[:dispatch_page_size+1]
    with transaction.atomic():
        try:
            for slip in slips:
                if i == dispatch_page_size+1:
                    has_more = True
                    # we have more so we need to spawn a new job
                    break

                message_id = client.get_message_id()
                slip.file.open(mode='rb')
                try:
                    resp = client.send_message(message=generator.generate_dispatch(slip.persontaxyear.person.cpr,
                                                                                   pdf_data=base64.b64encode(slip.file.read())),
                                               message_id=message_id)
                except ConnectionError:
                    job.result = {'error': 'ConnectionError'}
                    job.save(update_fields=['status', 'result'])
                    mark_parent_job_as_failed(job)
                except HTTPError as e:
                    error = {'error': 'HTTPError'}
                    # get json response or fallback to text response
                    if e.response is not None:
                        status_code = e.response.status_code
                        try:
                            error = {'status_code': status_code, 'error': e.response.json()}
                        except ValueError:
                            error = {'status_code': status_code, 'error': e.response.text}
                    job.status = 'failed'
                    job.result = error
                    slip.message_id = message_id
                    slip.save(update_fields=['message_id'])
                    job.save(update_fields=['status', 'result'])
                    mark_parent_job_as_failed(job)
                else:
                    recipient = resp.json()['recipients'][0]
                    # we only use 1 recipient
                    slip.message_id = message_id
                    slip.recipient_status = recipient['status']
                    if slip.recipient_status == 'dead':
                        # mark the message as failed
                        slip.status = 'failed'
                        slip.save(update_fields=['status', 'message_id'])
                    elif recipient['post_processing_status'] == '':
                        slip.status = 'sent'
                        slip.save(update_fields=['status', 'message_id'])
                    else:
                        slip.status = 'post_processing'
                        slip.save(update_fields=['status', 'message_id'])
                finally:
                    slip.file.close()
                i += 1

            with transaction.atomic():
                pending_slips = {slip.message_id: slip for slip in TaxSlipGenerated.objects.filter(
                    status='post_processing').filter(
                    persontaxyear__tax_year__pk=job.parent.arguments['year_pk']).select_for_update(skip_locked=True)[:50]}
                while pending_slips:
                    update_status_for_pending_dispatches(client, pending_slips)
                    pending_slips = {slip.message_id: slip for slip in TaxSlipGenerated.objects.filter(
                        status='post_processing').filter(
                        persontaxyear__tax_year__pk=job.parent.arguments['year_pk']).
                                                                           select_for_update(skip_locked=True)[:50]}
                    if pending_slips:
                        sleep(10)
        finally:
            client.close()

    with transaction.atomic():
        parent = Job.objects.filter(pk=job.parent.pk).select_for_update()[0]
        current_count = parent.arguments['current_count'] + min(i, dispatch_page_size)
        job.set_progress(current_count, parent.arguments['total_count'])
        if has_more is False:
            # if we are done mark the parent job as finished
            parent.progress = 100
            parent.end_at = timezone.now()
            parent.status = 'finished'
            parent.result = {'dispatched_items': current_count}
        parent.save()

    if has_more:
        Job.schedule_job(dispatch_eboks_tax_slips, 'dispatch_tax_year_child', job.parent.created_by, parent=job.parent)
