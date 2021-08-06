# -*- coding: utf-8 -*-
import base64
import traceback
from time import sleep

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import IntegerField, Sum, Q, Count
from django.db.models.functions import Cast
from django.db.utils import IntegrityError
from django.utils import timezone
from requests.exceptions import HTTPError, ConnectionError
from rq import get_current_job

from eskat.models import ImportedKasMandtal, ImportedR75PrivatePension
from eskat.models import MockModels, EskatModels
from kas.eboks import EboksClient, EboksDispatchGenerator
from kas.management.commands.create_initial_years import Command as CreateInitialYears
from kas.management.commands.import_default_pension_companies import Command as CreateInitialPensionComanies
from kas.models import Person, PersonTaxYear, TaxYear, PolicyTaxYear, PensionCompany, TaxSlipGenerated, \
    PreviousYearNegativePayout, FinalSettlement, PolicyDocument
from kas.models import PersonTaxYearCensus
from kas.reportgeneration.kas_final_statement import TaxFinalStatementPDF
from kas.reportgeneration.kas_report import TaxPDF
from prisme.models import Prisme10QBatch
from worker.job_registry import get_job_types, resolve_job_function
from worker.models import job_decorator, Job


@job_decorator
def import_mandtal(job):
    year = job.arguments['year']

    job.pretty_title = '%s - %s' % (job.pretty_job_type, year)
    job.save()

    tax_year = TaxYear.objects.get(year=year)
    number_of_progress_segments = 2
    progress_factor = 1 / number_of_progress_segments

    if job.arguments['source_model'] == "mockup":
        source_model = MockModels.MockKasMandtal
    elif job.arguments['source_model'] == "eskat":
        source_model = EskatModels.KasMandtal
    else:
        source_model = None

    mandtal_created, mandtal_updated = ImportedKasMandtal.import_year(
        year, job, progress_factor, 0,
        source_model=source_model
    )

    qs = ImportedKasMandtal.objects.filter(skatteaar=year)
    count = qs.count()
    progress_start = 50
    (persons_created, persons_updated) = (0, 0)
    (persontaxyears_created, persontaxyears_updated) = (0, 0)
    (persontaxyearcensus_created, persontaxyearcensus_updated) = (0, 0)

    with transaction.atomic():
        for i, item in enumerate(qs.iterator()):

            person_data = {
                'cpr': item.cpr,
                'name': item.navn,
                'municipality_name': item.kommune,
                'municipality_code': item.kommune_no,
                'address_line_1': item.adresselinje1,
                'address_line_2': item.adresselinje2,
                'address_line_3': item.adresselinje3,
                'address_line_4': item.adresselinje4,
                'address_line_5': item.adresselinje5,
                'full_address': item.fuld_adresse,
            }

            person, status = Person.update_or_create(person_data, 'cpr')
            if status == Person.CREATED:
                persons_created += 1
            elif status == Person.UPDATED:
                persons_updated += 1

            person_tax_year_data = {
                'person': person,
                'tax_year': tax_year,
                'number_of_days': 0,
                'fully_tax_liable': False,
            }

            person_tax_year, status = PersonTaxYear.update_or_create(person_tax_year_data, 'tax_year', 'person')
            if status == PersonTaxYear.CREATED:
                persontaxyears_created += 1
            elif status == PersonTaxYear.UPDATED:
                persontaxyears_updated += 1

            person_tax_year_census_data = {
                'person_tax_year': person_tax_year,
                'imported_kas_mandtal': item.pt_census_guid,
                'number_of_days': item.skattedage,
                'fully_tax_liable': item.skatteomfang is not None and item.skatteomfang.lower() == 'fuld skattepligtig',
            }
            person_tax_year_census, status = PersonTaxYearCensus.update_or_create(person_tax_year_census_data, 'person_tax_year', 'imported_kas_mandtal')
            if status == PersonTaxYear.CREATED:
                persontaxyearcensus_created += 1
            elif status == PersonTaxYear.UPDATED:
                persontaxyearcensus_updated += 1
            person_tax_year.recalculate_mandtal()

            if i % 1000 == 0:
                progress = progress_start + (i / count) * (100 * progress_factor)
                # Save this using 2nd db handle that is not inside the transaction
                job.set_progress_pct(progress, using='second_default')

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
        ]},
        {'label': 'Personskatteår-mandtal-objekter', 'value': [
            {'label': 'Tilføjet', 'value': persontaxyearcensus_created},
            {'label': 'Opdateret', 'value': persontaxyearcensus_updated}
        ]}
    ]}


@job_decorator
def import_r75(job):
    year = job.arguments['year']

    job.pretty_title = '%s - %s' % (job.pretty_job_type, year)
    job.save()

    tax_year = TaxYear.objects.get(year=year)
    number_of_progress_segments = 2
    progress_factor = 1 / number_of_progress_segments

    if job.arguments['source_model'] == "mockup":
        source_model = MockModels.MockR75Idx4500230
    elif job.arguments['source_model'] == "eskat":
        source_model = EskatModels.R75Idx4500230
    else:
        source_model = None

    (r75_created, r75_updated) = ImportedR75PrivatePension.import_year(
        year, job, progress_factor, 0,
        source_model=source_model
    )

    progress_start = 50
    (policies_created, policies_updated) = (0, 0)

    # This queryset groups results by cpr, res, ktd and creates an sum
    # of extra output field with the sum of the 'renteindtaegt' field.
    # It must be constructed with the calss in this order to generate
    # the correct SELECT .. GROUP BY .. query-
    qs = ImportedR75PrivatePension.objects.values(
        'cpr', 'res', 'ktd'
    ).filter(
        tax_year=year
    ).annotate(
        indtaegter_sum=Sum(Cast('renteindtaegt', output_field=IntegerField()))
    )
    count = qs.count()
    # mock data for autoligning
    value = None if job.arguments['source_model'] == "mockup" else True
    changed_by_citizen = value
    changed_by_clerk = value
    general_note_set = value
    with_documents = value
    rest_user = get_user_model().objects.get(username='rest')
    clerk_user = get_user_model().objects.exclude(username='rest').first()
    til_efterbahndling = []
    person, _ = Person.objects.get_or_create(cpr='1212121212', defaults={'name': 'Til efterbehandling'})
    person_tax_year, _ = PersonTaxYear.objects.get_or_create(person=person, tax_year=tax_year, number_of_days=365)
    company, _ = PensionCompany.objects.get_or_create(name='test123')
    # Created by citizen
    try:
        policy_tax_year = PolicyTaxYear(person_tax_year=person_tax_year,
                                        pension_company=company,
                                        policy_number=200,
                                        prefilled_amount=10000)
        policy_tax_year._history_user = rest_user  # fake creating through the res API
        policy_tax_year.save()
    except IntegrityError:
        #
        pass
    else:
        til_efterbahndling.append(policy_tax_year)

    with transaction.atomic():
        for i, item in enumerate(qs):
            person, c = Person.objects.get_or_create(cpr=item['cpr'])
            try:
                person_tax_year = PersonTaxYear.objects.get(
                    person=person, tax_year=tax_year,
                )

                res = int(item['res'])
                pension_company, c = PensionCompany.objects.get_or_create(**{'res': res})
                if c or pension_company.name in ('', None):
                    pension_company.name = f"Pensionsselskab med identifikationsnummer {res}"
                    pension_company.save()

                policy_data = {
                    'person_tax_year': person_tax_year,
                    'pension_company': pension_company,
                    'policy_number': item['ktd'],
                    'prefilled_amount': item['indtaegter_sum'],
                }
                (policy_tax_year, status) = PolicyTaxYear.update_or_create(policy_data, 'person_tax_year', 'pension_company', 'policy_number')
                if status in (PersonTaxYear.CREATED, PersonTaxYear.UPDATED):
                    policy_tax_year._change_reason = 'Updated by import'  # needed for autoligning
                    policy_tax_year.recalculate()
                    policy_tax_year.save()
                    policy_tax_year._change_reason = ''
                    if status == PersonTaxYear.CREATED:
                        policies_created += 1
                    elif status == PersonTaxYear.UPDATED:
                        policies_updated += 1

                if changed_by_citizen is None:
                    policy_tax_year.self_reported_amount = 300
                    policy_tax_year._history_user = rest_user  # changed by citizen
                    policy_tax_year.recalculate()
                    policy_tax_year.save()
                    changed_by_citizen = policy_tax_year
                elif changed_by_clerk is None:
                    policy_tax_year.self_reported_amount = 600
                    policy_tax_year._history_user = clerk_user  # changed by clerk
                    policy_tax_year.recalculate()
                    policy_tax_year.save()
                    changed_by_clerk = policy_tax_year
                elif general_note_set is None:
                    policy_tax_year.general_notes = 'this is a general note'
                    policy_tax_year.save()
                    general_note_set = policy_tax_year
                elif with_documents is None:
                    # Create empty document
                    with_documents = PolicyDocument.objects.create(person_tax_year=person_tax_year,
                                                                   name='test', description='Trigger to efterbhandling')

            except PersonTaxYear.DoesNotExist:
                pass

            if i % 100 == 0:
                progress = progress_start + (i / count) * (100 * progress_factor)
                # Save progress using 2nd db handle not affected by transaction
                job.set_progress_pct(progress, using='second_default')

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


@job_decorator
def generate_reports_for_year(job):
    qs = PersonTaxYear.get_pdf_recipients_for_year_qs(
        job.arguments['year_pk'],
        exclude_already_generated=True
    )
    total_count = qs.count()
    for i, person_tax_year in enumerate(qs.iterator(), 1):
        pdf_generator = TaxPDF()  # construct a new pdf generator everytime to start a new pdf file
        pdf_generator.perform_complete_write_of_one_person_tax_year(person_tax_year, title=job.arguments['title'])
        job.set_progress(i, total_count)


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
                message = pending_messages[message['message_id']]
                message.post_processing_status = recipient['post_processing_status']
                message.status = 'send'
                message.save(update_fields=['post_processing_status', 'status'])


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
    generator = EboksDispatchGenerator.from_settings()
    client = EboksClient.from_settings()
    i = 1
    has_more = False
    slips = TaxSlipGenerated.objects.filter(status='created').filter(
        persontaxyear__tax_year__pk=job.parent.arguments['year_pk'])[:dispatch_page_size+1]
    try:
        for slip in slips:
            if i == dispatch_page_size+1:
                has_more = True
                # we have more so we need to spawn a new job
                break

            message_id = client.get_message_id()
            slip.file.open(mode='rb')
            try:
                resp = client.send_message(message=generator.generate_dispatch(slip.title,
                                                                               slip.persontaxyear.person.cpr,
                                                                               pdf_data=base64.b64encode(slip.file.read())),
                                           message_id=message_id)
            except (ConnectionError, HTTPError) as e:
                job.status = 'failed'
                job.result = client.parse_exception(e)
                job.save(update_fields=['status', 'result'])
                mark_parent_job_as_failed(job)
                break
            else:
                # we only use 1 recipient
                json = resp.json()
                recipient = json['recipients'][0]
                slip.message_id = json['message_id']  # message_id might have changed so get it from the response
                slip.recipient_status = recipient['status']
                slip.send_at = timezone.now()
                if recipient['post_processing_status'] == '':
                    slip.status = 'send'
                else:
                    slip.status = 'post_processing'
                slip.save(update_fields=['status', 'message_id', 'recipient_status', 'send_at'])
            finally:
                slip.file.close()
            i += 1

        pending_slips = {slip.message_id: slip for slip in TaxSlipGenerated.objects.filter(
            status='post_processing').filter(
            persontaxyear__tax_year__pk=job.parent.arguments['year_pk'])[:50]}
        while pending_slips:
            update_status_for_pending_dispatches(client, pending_slips)
            pending_slips = {slip.message_id: slip for slip in TaxSlipGenerated.objects.filter(
                status='post_processing').filter(
                persontaxyear__tax_year__pk=job.parent.arguments['year_pk'])[:50]}
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
            parent.finish(result={'dispatched_items': current_count})

    if has_more:
        Job.schedule_job(dispatch_eboks_tax_slips, 'dispatch_tax_year_child', job.parent.created_by, parent=job.parent)


@job_decorator
def clear_test_data(job):
    if settings.ENVIRONMENT == "production":
        raise Exception("Will not clear data in production")

    for model in (
        ImportedKasMandtal,
        ImportedR75PrivatePension,
        MockModels.MockKasMandtal,
        MockModels.MockR75Idx4500230,
        PreviousYearNegativePayout,
        PolicyTaxYear,
        PersonTaxYear,
        Person,
        TaxYear,
        PensionCompany,
    ):
        model.objects.all().delete()

    CreateInitialYears().handle()
    CreateInitialPensionComanies().handle()

    return {
        'status': 'OK',
        'message': 'Data nulstillet',
    }


def dispatch_chained_jobs(list_of_jobs, parent_job):
    total_jobs = len(list_of_jobs)

    parent_job.pretty_title = '%s - %s jobs' % (parent_job.pretty_job_type, total_jobs)

    previous_job = None
    for i, pair in enumerate(list_of_jobs):
        job_type, arguments = pair
        job_data = get_job_types()[job_type]
        function = resolve_job_function(job_data['function'])

        new_job = Job.schedule_job(
            function=function,
            job_type=job_type,
            created_by=parent_job.created_by,
            parent=parent_job,
            depends_on=previous_job,
            job_kwargs=arguments
        )
        previous_job = new_job

    return {
        'status': 'OK',
        'message': '%d jobs scheduled' % (total_jobs),
    }


@job_decorator
def reset_to_mockup_data(job):

    subjobs = [
        ('ImportEskatMockup', job.arguments),
        ('ImportAllMockupMandtal', job.arguments),
        ('ImportAllMockupR75', job.arguments),
    ]

    # Unless explicitly told to not delete stuff add job at start that deletes everything
    if not job.arguments.get('skip_deletions'):
        subjobs = [('ClearTestData', job.arguments)] + subjobs

    dispatch_chained_jobs(subjobs, job)


@job_decorator
def import_all_mandtal(job):
    jobs = [
        ('ImportMandtalJob', {'source_model': 'mockup', 'year': tax_year.year})
        for tax_year in TaxYear.objects.order_by('year')
    ]

    dispatch_chained_jobs(jobs, job)


@job_decorator
def import_all_r75(job):
    jobs = [
        ('ImportR75Job', {'source_model': 'mockup', 'year': tax_year.year})
        for tax_year in TaxYear.objects.order_by('year')
    ]

    dispatch_chained_jobs(jobs, job)


def check_year_period(year, job, periode):
    """
    Checks that the year is in the correct periode otherwise logs the error on the job
    :param year: the year to check
    :param job: the executed job
    :param periode: the periode to check
    """
    if year.year_part != periode:
        job.status = 'failed'
        job.result = {'error': 'Kan kun {title} år som er i perioden {periode}'.format(title=job.pretty_title,
                                                                                       periode=periode)}
        job.end_at = timezone.now()
        job.save(update_fields=['status', 'result', 'end_at'])
        return False
    return True


@job_decorator
def autoligning(job):
    """Kør autoligning for et given år"""
    year = TaxYear.objects.get(pk=job.arguments['year_pk'])
    if not check_year_period(year, job, 'selvangivelse'):
        return

    # if no user is found this will raise an exception which is what we want
    rest_user = get_user_model().objects.get(username='rest')

    with transaction.atomic():
        policies = PolicyTaxYear.objects.select_related(
            'person_tax_year').filter(active=True, person_tax_year__tax_year=year).select_for_update()
        autolignet = 0
        post_processing = 0
        total = 0
        for policy in policies:
            if policy.history.filter((Q(history_type='~',) & ~ Q(
                    history_change_reason='Updated by import')) | Q(
                        history_type='+', history_user=rest_user)).exists():

                # policy has changes or policy was created by citizen
                policy.efterbehandling = True
                policy.slutlignet = False
                post_processing += 1
            elif policy.person_tax_year.general_notes and len(policy.person_tax_year.general_notes.replace(' ', '')) > 0:
                # General note on PersonTaxYear is not null and contains at least 1 character
                policy.efterbehandling = True
                policy.slutlignet = False
                post_processing += 1
            elif policy.person_tax_year.notes.exists() or policy.person_tax_year.policydocument_set.exists():
                # notes or documents was created for the related person_tax_year
                policy.efterbehandling = True
                policy.slutlignet = False
                post_processing += 1
            else:
                policy.efterbehandling = False
                policy.slutlignet = True
                autolignet += 1

            # Make sure assessed_amount is stored in the database
            policy.assessed_amount = policy.get_assessed_amount()

            # Recalculate used negative amounts etc.
            policy.recalculate()

            total += 1
            policy._change_reason = 'autoligning'
            policy._history_user = job.created_by
            policy.save()

        year.year_part = 'ligning'
        year.save()

        result = {'autolignet': autolignet,
                  'post_processing': post_processing,
                  'total': total}
        job.finish(result)


@job_decorator
def generate_final_settlements_for_year(job):
    """
    For each person tax year generate a final settlement if:
    person_tax_year is fully tab liable and
    there exists one or more active and slutlignet policies.
    """
    tax_year = TaxYear.objects.get(pk=job.arguments['year_pk'])
    if not check_year_period(tax_year, job, 'ligning'):
        return

    generated_final_settlements = 0

    qs = PersonTaxYear.objects.filter(
        tax_year=tax_year,
        fully_tax_liable=True
    ).annotate(
        active_policies=Count('policytaxyear', filter=Q(policytaxyear__active=True, policytaxyear__slutlignet=True))
    ).filter(active_policies__gt=0)
    for person_tax_year in qs.iterator():
        TaxFinalStatementPDF.generate_pdf(person_tax_year=person_tax_year)
        generated_final_settlements += 1

    job.finish({'status': 'Genererede slutopgørelser', 'message': generated_final_settlements})


@job_decorator
def generate_batch_and_transactions_for_year(job):
    tax_year = TaxYear.objects.get(pk=job.arguments['year_pk'])
    if not check_year_period(tax_year, job, 'ligning'):
        return
    batch = Prisme10QBatch.objects.create(created_by=job.created_by,
                                          tax_year=tax_year)
    settlements = FinalSettlement.objects.filter(person_tax_year__tax_year=tax_year, invalid=False)
    settlements_count = 0
    new_transactions = 0
    for final_settlement in settlements:
        settlements_count += 1
        if final_settlement.get_transaction_amount() != 0:
            batch.add_transaction(final_settlement)
            new_transactions += 1

    job.finish({'status': 'Genererede batch og transaktioner',
                'message': 'Genererede {transactions} på baggrund af {settlements} slutopgørelser'.format(transactions=new_transactions,
                                                                                                          settlements=settlements_count)})


def dispatch_final_settlements_for_year():
    rq_job = get_current_job()
    with transaction.atomic():
        job = Job.objects.select_for_update().filter(uuid=rq_job.meta['job_uuid'])[0]
        job.status = rq_job.get_status()
        job.progress = 0
        job.started_at = timezone.now()
        settlements = FinalSettlement.objects.exclude(invalid=True).filter(status='created'). \
            filter(person_tax_year__tax_year__pk=job.arguments['year_pk'])
        settlements.update(title=job.arguments['title'])
        job.arguments['total_count'] = settlements.count()
        job.arguments['current_count'] = 0
        job.save(update_fields=['status', 'progress', 'started_at', 'arguments'])

    if job.arguments['total_count'] > 0:
        Job.schedule_job(dispatch_final_settlements, 'dispatch_final_settlements_child', job.created_by, parent=job)
    else:
        job.finish()


@job_decorator
def dispatch_final_settlements(job):
    from django.conf import settings
    dispatch_page_size = settings.EBOKS['dispatch_bulk_size']
    generator = EboksDispatchGenerator.from_settings()
    client = EboksClient.from_settings()
    has_more = False
    settlements = FinalSettlement.objects.exclude(invalid=True).filter(
        status='created').filter(person_tax_year__tax_year__pk=job.parent.arguments['year_pk'])[:dispatch_page_size+1]

    pending_messages = {}
    current_number_of_items = 0
    for i, settlement in enumerate(settlements, start=1):
        if i == dispatch_page_size+1:
            has_more = True
            # we have more so we need to spawn a new job
            break
        try:
            send_settlement = settlement.dispatch_to_eboks(client, generator)
        except (ConnectionError, HTTPError) as e:
            job.status = 'failed'
            job.result = client.parse_exception(e)
            job.traceback = repr(traceback.format_exception(type(e), e, e.__traceback__))
            job.save(update_fields=['status', 'result', 'traceback'])
            mark_parent_job_as_failed(job)
            break
        else:
            if send_settlement.status == 'post_processing':
                pending_messages[send_settlement.message_id] = send_settlement
            current_number_of_items = i

    while pending_messages:
        update_status_for_pending_dispatches(client, pending_messages)
        pending_messages = {settlement.message_id: settlement for settlement in FinalSettlement.objects.filter(
            status='post_processing', person_tax_year__tax_year__pk=job.parent.arguments['year_pk'])[:50]}
        if pending_messages:
            sleep(10)

    with transaction.atomic():
        parent = Job.objects.filter(pk=job.parent.pk).select_for_update()[0]
        current_count = parent.arguments['current_count'] + min(current_number_of_items, dispatch_page_size)
        job.set_progress(current_count, parent.arguments['total_count'])
        if not has_more:
            if job.status != 'failed':
                # set the current year part to genoptagelse only if job didnt fail
                year = TaxYear.objects.get(pk=parent.arguments['year_pk'])
                year.year_part = 'genoptagelsesperiode'
                year.save(update_fields=['year_part'])

            # mark the parent job as finished
            parent.finish(result={'dispatched_items': current_count})

    if has_more:
        # start a new child job to handle the next hundred
        Job.schedule_job(dispatch_final_settlements,
                         'dispatch_final_settlements_child',
                         job.parent.created_by,
                         parent=job.parent)


@job_decorator
def dispatch_final_settlement(job):
    """
    expects a final_settlmenet uuid
    :return:
    """
    client = EboksClient.from_settings()
    settlement = FinalSettlement.objects.get(uuid=job.arguments['uuid'])
    generator = EboksDispatchGenerator.from_settings()
    send_settlement = settlement.dispatch_to_eboks(client, generator)
    if send_settlement.status == 'post_processing':
        job.set_progress_pct(50)
        send_settlement.get_final_status(client)
    job.finish()


@job_decorator
def force_finalize_settlement(job):
    """
    Forces all outstanding policies to be finalized
    :return:
    """
    policies = PolicyTaxYear.objects.filter(
        slutlignet=False,
        person_tax_year__tax_year__pk=job.arguments['year_pk']
    )
    count = policies.count()
    for i, policy in enumerate(policies.iterator(), start=1):
        policy.slutlignet = True
        policy.efterbehandling = True
        policy._change_reason = 'Forced finalization'
        policy._history_user = job.created_by
        policy.save()
        job.set_progress(i, count)
    job.finish()
