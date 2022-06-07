from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from kas.models import TaxYear, PensionCompany, Person, PolicyTaxYear, PersonTaxYear

from prisme.models import Prisme10QBatch, Transaction

from kas.models import FinalSettlement


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = 'test'
        self.user.set_password(self.password)
        self.user.save()
        # add user to administrator group
        self.administrator_group = Group.objects.get(name='administrator')
        self.user.groups.set([self.administrator_group])
        self.tax_year = TaxYear.objects.create(year=2021)
        self.person = Person.objects.create(cpr='1234567890', name='TestPerson')
        self.person_tax_year = PersonTaxYear.objects.create(tax_year=self.tax_year,
                                                            person=self.person,
                                                            number_of_days=1)
        self.pension_company = PensionCompany.objects.create()
        self.policy_tax_year = PolicyTaxYear.objects.create(person_tax_year=self.person_tax_year,
                                                            pension_company=self.pension_company,
                                                            prefilled_amount=35,
                                                            policy_number='1234',
                                                            )

    def self_report_policy_tax_year(self):
        self.policy_tax_year.self_reported_amount = 1000
        self.policy_tax_year.active_amount = PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED
        self.policy_tax_year.recalculate()
        self.policy_tax_year.save()


class SelfReportedAmountUpdateViewTestCase(BaseTestCase):

    def test_not_logged_in(self):
        r = self.client.get(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]))
        # should redirect to login page
        self.assertEqual(r.status_code, 302)

    def test_valid_get(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.get(reverse('kas:change-self-reported-amount', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.status_code, 200)

    def test_invalid_urls(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.get(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk+1]))
        self.assertEqual(r.status_code, 404)

    def test_form_submit(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.post(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]),
                             follow=True,
                             data={'self_reported_amount': 99,
                                   'notes-TOTAL_FORMS': 1,
                                   'notes-INITIAL_FORMS': 0,
                                   'uploads-TOTAL_FORMS': 1,
                                   'uploads-INITIAL_FORMS': 0})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertEqual(policy_tax_year.self_reported_amount, 99)
        self.assertFalse(policy_tax_year.notes.exists())
        self.assertFalse(policy_tax_year.person_tax_year.notes.exists())
        self.assertFalse(policy_tax_year.policy_documents.exists())
        self.assertFalse(policy_tax_year.person_tax_year.policydocument_set.exists())

    def test_submit_note(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.post(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]),
                             follow=True,
                             data={'self_reported_amount': 99,
                                   'notes-TOTAL_FORMS': 1,
                                   'notes-0-content': 'test',
                                   'notes-INITIAL_FORMS': 0,
                                   'uploads-TOTAL_FORMS': 1,
                                   'uploads-INITIAL_FORMS': 0})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertTrue(policy_tax_year.person_tax_year.all_documents_and_notes_handled)
        self.assertEqual(policy_tax_year.self_reported_amount, 99)
        self.assertEqual(policy_tax_year.notes.count(), 1)
        self.assertEqual(policy_tax_year.notes.first().author, self.user)
        self.assertEqual(policy_tax_year.person_tax_year.notes.count(), 1)
        self.assertFalse(policy_tax_year.policy_documents.exists())
        self.assertFalse(policy_tax_year.person_tax_year.policydocument_set.exists())

    def test_submit_document(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.post(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]),
                             follow=True,
                             data={'self_reported_amount': 99,
                                   'notes-TOTAL_FORMS': 1,
                                   'notes-INITIAL_FORMS': 0,
                                   'uploads-TOTAL_FORMS': 1,
                                   'uploads-0-description': 'test_description',
                                   'uploads-0-file': SimpleUploadedFile(name='test', content=b'test_submit_document'),
                                   'uploads-INITIAL_FORMS': 0})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertTrue(policy_tax_year.person_tax_year.all_documents_and_notes_handled)
        self.assertEqual(policy_tax_year.self_reported_amount, 99)
        self.assertFalse(policy_tax_year.notes.exists())
        self.assertFalse(policy_tax_year.person_tax_year.notes.exists())
        self.assertEquals(policy_tax_year.policy_documents.count(), 1)
        self.assertEquals(policy_tax_year.person_tax_year.policydocument_set.count(), 1)
        policy_documents = policy_tax_year.policy_documents.first()
        self.assertEqual(policy_documents.uploaded_by, self.user)

    def test_submit_note_and_document(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.post(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]),
                             follow=True,
                             data={'self_reported_amount': 99,
                                   'notes-TOTAL_FORMS': 1,
                                   'notes-INITIAL_FORMS': 0,
                                   'notes-0-content': 'test',
                                   'uploads-TOTAL_FORMS': 1,
                                   'uploads-0-description': 'test_description',
                                   'uploads-0-file': SimpleUploadedFile(name='test', content=b'test_submit_note_and_document'),
                                   'uploads-INITIAL_FORMS': 0})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertTrue(policy_tax_year.person_tax_year.all_documents_and_notes_handled)
        self.assertEqual(policy_tax_year.self_reported_amount, 99)
        self.assertEqual(policy_tax_year.notes.count(), 1)
        self.assertEqual(policy_tax_year.notes.first().author, self.user)
        self.assertEqual(policy_tax_year.person_tax_year.notes.count(), 1)
        self.assertEquals(policy_tax_year.policy_documents.count(), 1)
        self.assertEquals(policy_tax_year.person_tax_year.policydocument_set.count(), 1)
        policy_documents = policy_tax_year.policy_documents.first()
        self.assertEqual(policy_documents.uploaded_by, self.user)


class EditAmountsUpdateViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(EditAmountsUpdateViewTestCase, self).setUp()
        self.tax_year.year_part = 'ligning'
        self.tax_year.save()
        self.client.login(username=self.username, password=self.password)

    def test_not_logged_in(self):
        self.client.logout()
        r = self.client.get(reverse('kas:change-edit-amounts', args=[self.policy_tax_year.pk]))
        # should redirect to login page
        self.assertEqual(r.status_code, 302)

    def test_valid_get(self):
        r = self.client.get(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.status_code, 200)

    def test_self_reported_amount(self):
        self.policy_tax_year.self_reported_amount = 924
        self.policy_tax_year.save()
        r = self.client.get(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.context['form']['assessed_amount'].value(), 924)
        self.assertEqual(r.context['form']['adjusted_r75_amount'].value(), 35)

    def test_adjusted_r75_amount(self):
        self.policy_tax_year.adjusted_r75_amount = 501
        self.policy_tax_year.save()
        r = self.client.get(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.context['form']['assessed_amount'].value(), 501)
        self.assertEqual(r.context['form']['adjusted_r75_amount'].value(), 501)

    def test_prefilled_amount(self):
        r = self.client.get(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.context['form']['assessed_amount'].value(), 35)
        self.assertEqual(r.context['form']['adjusted_r75_amount'].value(), 35)

    def test_set_efterbehandling_by_self_reported_amount(self):
        r = self.client.post(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}),
                             follow=True,
                             data={'notes-TOTAL_FORMS': 0,
                                   'notes-INITIAL_FORMS': 0,
                                   'uploads-TOTAL_FORMS': 0,
                                   'uploads-INITIAL_FORMS': 0,
                                   'self_reported_amount': 200})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertTrue(policy_tax_year.efterbehandling)

    def test_set_efterbehandling_by_note(self):
        r = self.client.post(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}),
                             follow=True,
                             data={'notes-TOTAL_FORMS': 1,
                                   'notes-INITIAL_FORMS': 0,
                                   'notes-0-content': 'test',
                                   'uploads-TOTAL_FORMS': 0,
                                   'uploads-INITIAL_FORMS': 0,
                                   })
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertTrue(policy_tax_year.efterbehandling)

    def test_set_efterbehandling_by_attachment(self):
        r = self.client.post(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}),
                             follow=True,
                             data={'notes-TOTAL_FORMS': 1,
                                   'notes-INITIAL_FORMS': 0,
                                   'uploads-TOTAL_FORMS': 1,
                                   'uploads-INITIAL_FORMS': 0,
                                   'uploads-0-description': 'test_description',
                                   'uploads-0-file': SimpleUploadedFile(name='test', content=b'test_set_efterbehandling_by_attachment')})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertTrue(policy_tax_year.efterbehandling)

    def test_set_slutlignet_clears_efterbehandling(self):
        self.policy_tax_year.efterbehandling = True
        self.policy_tax_year.save()
        r = self.client.post(reverse('kas:change-edit-amounts', args=[self.policy_tax_year.pk]),
                             follow=True,
                             data={'slutlignet': True,
                                   'notes-TOTAL_FORMS': 0,
                                   'notes-INITIAL_FORMS': 0,
                                   'uploads-TOTAL_FORMS': 0,
                                   'uploads-INITIAL_FORMS': 0,
                                   'self_reported_amount': 300})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        # Efterbehandling should still be true since we cannot unset it using the form.
        self.assertTrue(policy_tax_year.slutlignet)
        self.assertFalse(policy_tax_year.efterbehandling)


class PolicyNotesAndAttachmentsViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(PolicyNotesAndAttachmentsViewTestCase, self).setUp()
        self.client.login(username=self.username, password=self.password)

    def test_not_logged_in(self):
        self.client.logout()
        r = self.client.get(reverse('kas:policy_add_notes_or_attachement', args=[self.policy_tax_year.pk]))
        # should redirect to login page
        self.assertEqual(r.status_code, 302)

    def _check_status(self, policy_tax_year):
        # ensure the policy tax years status is set correctly when the processing_date is changed
        # or documents/notes are added
        self.assertEqual(policy_tax_year.efterbehandling, True)
        self.assertEqual(policy_tax_year.slutlignet, False)
        self.assertTrue(policy_tax_year.person_tax_year.all_documents_and_notes_handled)

    def test_save_note(self):
        note_string = 'this is a note 456'
        self.client.post(reverse('kas:policy_add_notes_or_attachement', args=[self.policy_tax_year.pk]),
                         follow=True,
                         data={'note': note_string})
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertEqual(policy_tax_year.notes.count(), 1)
        self.assertEqual(policy_tax_year.notes.first().content, note_string)
        self._check_status(policy_tax_year)

    def test_save_attachment(self):
        attachment_description = 'this is a test file'
        self.client.post(reverse('kas:policy_add_notes_or_attachement', args=[self.policy_tax_year.pk]),
                         follow=True,
                         data={'attachment': SimpleUploadedFile(name='test', content=b'test_save_attachment'),
                               'attachment_description': attachment_description})
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertEqual(policy_tax_year.policy_documents.count(), 1)
        document = policy_tax_year.policy_documents.first()
        self.assertEqual(document.description, attachment_description)
        self._check_status(policy_tax_year)

    def test_set_processing_date(self):
        next_processing_date = (timezone.now()+timedelta(days=2)).date()
        self.client.post(reverse('kas:policy_add_notes_or_attachement', args=[self.policy_tax_year.pk]),
                         follow=True,
                         data={'next_processing_date': next_processing_date})
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertEqual(policy_tax_year.next_processing_date, next_processing_date)
        self._check_status(policy_tax_year)

    def test_change_processing_date(self):
        self.policy_tax_year.next_processing_date = (timezone.now()+timedelta(days=2)).date()
        self.policy_tax_year.save()
        next_processing_date = (timezone.now()+timedelta(days=5)).date()
        self.client.post(reverse('kas:policy_add_notes_or_attachement', args=[self.policy_tax_year.pk]),
                         follow=True,
                         data={'next_processing_date': next_processing_date})
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertEqual(policy_tax_year.next_processing_date, next_processing_date)
        self._check_status(policy_tax_year)


class PersonNotesAndAttachmentsViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(PersonNotesAndAttachmentsViewTestCase, self).setUp()
        self.client.login(username=self.username, password=self.password)

    def test_not_logged_in(self):
        self.client.logout()
        r = self.client.get(reverse('kas:person_add_notes_or_attachement', args=[self.person_tax_year.pk]))
        # should redirect to login page
        self.assertEqual(r.status_code, 302)

    def test_add_note(self):
        note_string = 'this is a note 6234325'
        self.client.post(reverse('kas:person_add_notes_or_attachement', args=[self.person_tax_year.pk]),
                         follow=True,
                         data={'note': note_string})
        person_tax_year = PersonTaxYear.objects.get(pk=self.person_tax_year.pk)
        self.assertEqual(person_tax_year.notes.count(), 1)
        self.assertEqual(person_tax_year.notes.first().content, note_string)
        self.assertFalse(person_tax_year.all_documents_and_notes_handled)

    def test_save_attachment(self):
        attachment_description = 'this is a test file 1531253'
        self.client.post(reverse('kas:person_add_notes_or_attachement', args=[self.person_tax_year.pk]),
                         follow=True,
                         data={'attachment': SimpleUploadedFile(name='test', content=b'test_save_attachment'),
                               'attachment_description': attachment_description})

        person_tax_year = PersonTaxYear.objects.get(pk=self.person_tax_year.pk)
        self.assertEqual(person_tax_year.policydocument_set.count(), 1)
        document = person_tax_year.policydocument_set.first()
        self.assertEqual(document.description, attachment_description)
        self.assertFalse(person_tax_year.all_documents_and_notes_handled)

    def test_save_attachment_and_note(self):
        note_string = 'this is a note 6234325'
        attachment_description = 'this is a test file 1531253'
        self.client.post(reverse('kas:person_add_notes_or_attachement', args=[self.person_tax_year.pk]),
                         follow=True,
                         data={'attachment': SimpleUploadedFile(name='test', content=b'test_save_attachment_and_note'),
                               'attachment_description': attachment_description,
                               'note': note_string})
        person_tax_year = PersonTaxYear.objects.get(pk=self.person_tax_year.pk)
        self.assertEqual(person_tax_year.notes.count(), 1)
        self.assertEqual(person_tax_year.notes.first().content, note_string)
        self.assertEqual(person_tax_year.policydocument_set.count(), 1)
        document = person_tax_year.policydocument_set.first()
        self.assertEqual(document.description, attachment_description)
        self.assertFalse(person_tax_year.all_documents_and_notes_handled)


class PaymentOverrideTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(PaymentOverrideTestCase, self).setUp()
        self.client.login(username=self.username, password=self.password)
        self.management_form_data = {
            'notes-TOTAL_FORMS': 0,
            'notes-INITIAL_FORMS': 0,
            'uploads-TOTAL_FORMS': 0,
            'uploads-INITIAL_FORMS': 0,
        }

    def test_not_logged_in(self):
        self.client.logout()
        r = self.client.get(reverse('kas:policy_payment_override', args=[self.policy_tax_year.pk]))
        # should redirect to login page
        self.assertEqual(r.status_code, 302)

    def test_no_override(self):
        self.pension_company.agreement_present = False
        self.assertFalse(self.policy_tax_year.pension_company_pays)

        self.pension_company.agreement_present = True
        self.pension_company.save()
        self.assertTrue(self.policy_tax_year.pension_company_pays)

        self.client.post(
            reverse('kas:policy_payment_override', args=[self.policy_tax_year.pk]),
            follow=True,
            data={
                'citizen_pay_override': False,
                **self.management_form_data
            }
        )
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertTrue(policy_tax_year.pension_company_pays)
        self.assertFalse(policy_tax_year.efterbehandling)

    def test_override(self):

        self.assertFalse(self.policy_tax_year.efterbehandling)
        self.pension_company.agreement_present = True
        self.assertTrue(self.policy_tax_year.pension_company_pays)

        self.client.post(
            reverse('kas:policy_payment_override', args=[self.policy_tax_year.pk]),
            follow=False,
            data={
                'citizen_pay_override': True,
                **self.management_form_data
            }
        )
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertFalse(policy_tax_year.pension_company_pays)
        self.assertTrue(policy_tax_year.efterbehandling)

    def test_remove_override(self):

        self.assertFalse(self.policy_tax_year.efterbehandling)
        self.pension_company.agreement_present = True
        self.pension_company.save()
        self.policy_tax_year.citizen_pay_override = True
        self.policy_tax_year.save()

        self.client.post(
            reverse('kas:policy_payment_override', args=[self.policy_tax_year.pk]),
            follow=False,
            data={
                'citizen_pay_override': False,
                **self.management_form_data
            }
        )
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertTrue(policy_tax_year.pension_company_pays)
        self.assertTrue(policy_tax_year.efterbehandling)

    def test_generate_final_taxslip(self):
        self.self_report_policy_tax_year()
        # Tested function wants the tax_year to be in 'genoptagelsesperiode'
        self.tax_year.year_part = 'genoptagelsesperiode'
        self.tax_year.save()

        self.assertTrue(self.client.login(username=self.username, password=self.password))
        response = self.client.post(
            reverse('kas:generate-final-settlement', kwargs={'pk': self.person_tax_year.pk}),
            {
                'interest_on_remainder': '0.0',
                'extra_payment_for_previous_missing': '0',
                'text_used_for_payment': FinalSettlement.PAYMENT_TEXT_DUE_ON_DATE
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Prisme10QBatch.objects.count(), 1)
        batch = Prisme10QBatch.objects.first()
        self.assertEqual(batch.created_by, self.user)
        self.assertEqual(batch.tax_year, self.tax_year)
        self.assertEqual(FinalSettlement.objects.count(), 1)
        statement = FinalSettlement.objects.first()
        self.assertEqual(statement.person_tax_year, self.person_tax_year)
        self.assertFalse(statement.invalid)

        # Cruder way of calculating the current date + 3 months + until next month
        # because calculating the same way as the tested function proves nothing (if they were identical but wrong, we wouldn't catch it)
        collect_date = date.today()
        # Always add 4 months to the 1st of the current month
        collect_date = collect_date.replace(day=1, month=((collect_date.month+3) % 12) + 1)

        # If we wrapped around to a month lower than the current one, we shold add a year
        if collect_date.month < date.today().month:
            collect_date = collect_date.replace(year=collect_date.year + 1)

        self.assertEqual(batch.collect_date, collect_date)
        self.assertEqual(self.person_tax_year.transaction_set.count(), 1)
        transaction = self.person_tax_year.transaction_set.first()
        self.assertEqual(transaction.person_tax_year, self.person_tax_year)
        self.assertEqual(transaction.amount, self.policy_tax_year.calculated_result)
        self.assertEqual(transaction.type, 'prisme10q')
        self.assertEqual(transaction.status, 'created')
        self.assertEqual(transaction.prisme10Q_batch, batch)


class CreateLockForYearTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(CreateLockForYearTestCase, self).setUp()
        self.client.login(username=self.username, password=self.password)

    def test_allow_closing(self):
        r = self.client.get(reverse('kas:lock-create')+f'?taxyear={self.tax_year.pk}')
        self.assertEqual(r.status_code, 200)
        # object is the taxyear
        self.assertFalse(self.tax_year.locks.exclude(interval_to__isnull=True).exists())
        self.assertTrue(r.context['object'].get_current_lock.allow_closing)

    def test_create_new_lock(self):
        self.assertFalse(self.tax_year.locks.exclude(interval_to__isnull=True).exists())
        r = self.client.post(reverse('kas:lock-create'), data={'taxyear': self.tax_year.pk}, follow=True)
        self.assertEqual(r.status_code, 200)
        # one open and one locked
        self.assertEqual(self.tax_year.locks.count(), 2)
        # 1 open lock
        self.assertEqual(self.tax_year.locks.filter(interval_to__isnull=True).count(), 1)
        # 1 closed lock
        self.assertEqual(self.tax_year.locks.exclude(interval_to__isnull=True).count(), 1)

    def test_new_open_lock_is_disallowed(self):
        self.self_report_policy_tax_year()
        settlement = FinalSettlement.objects.create(person_tax_year=self.person_tax_year,
                                                    lock=self.tax_year.get_current_lock)
        # Create pending transaction
        new_entry = Transaction.objects.create(
            person_tax_year=self.person_tax_year,
            amount=100,
            type='prisme10q',
            source_object=settlement,
            summary=settlement.get_transaction_summary(),
        )
        self.assertFalse(self.tax_year.get_current_lock.allow_closing)
        r = self.client.post(reverse('kas:lock-create'), data={'taxyear': self.tax_year.pk}, follow=True)
        self.assertEqual(r.status_code, 200)
        # No lock was create 
        self.assertEqual(self.tax_year.locks.count(), 1)
