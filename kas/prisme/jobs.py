import io
from csv import DictReader

from kas.models import PersonTaxYear
from prisme.models import PrePaymentFile, Transaction
from worker.models import job_decorator
from django.utils import timezone


@job_decorator
def import_pre_payment_file(job):
    pre_payment_file = PrePaymentFile.objects.get(pk=job.arguments['pk'])
    fields = [None, 'cpr_number', None, 'payment_year', 'amount', None, None, 'unique_id']
    with pre_payment_file.file.open(mode='rb'):
        with io.TextIOWrapper(pre_payment_file.file, encoding='ISO-8859-1') as text_file:
            reader = DictReader((line.replace('\0', '') for line in text_file), delimiter=';', fieldnames=fields)
            errors = []
            created_transactions = []
            rows = list(reader)
            row_count = len(rows)
            for i, row in enumerate(rows, start=0):
                # Make sure CPR number has leading zeroes
                cpr = str(row['cpr_number']).rjust(10, '0')
                try:
                    person_tax_year = PersonTaxYear.objects.get(person__cpr=cpr,
                                                                tax_year__year=row['payment_year'])
                except PersonTaxYear.DoesNotExist:
                    errors.append('Personskatteår eksisterer ikke for {cpr} i år {year}'.format(cpr=cpr,
                                                                                                year=row['payment_year']))
                else:
                    transaction = Transaction.objects.create(
                        person_tax_year=person_tax_year,
                        amount=int(row['amount']),
                        type='prepayment',
                        source_object=pre_payment_file,
                        status='transferred',
                    )
                    created_transactions.append({'transaction': str(transaction),
                                                 'person': transaction.person_tax_year.person.pk,
                                                 'year': transaction.person_tax_year.year})
                finally:
                    job.set_progress(i, row_count)
            job.result = {'created_transactions': created_transactions, 'errors': errors}
