
from django.test import TestCase
from kas.models import TaxYear, Lock, PersonTaxYear, Person
from kas.models import FinalSettlement


class TestLockSystem(TestCase):

    def setUp(self):
        super().setUp()

        self.taxyear2020 = TaxYear.objects.create(year=2020)
        self.taxyear2021 = TaxYear.objects.create(year=2021)

        self.old_lock_2020 = self.taxyear2020.lock_set.get(interval_to=None)
        self.old_lock_2021 = self.taxyear2021.lock_set.get(interval_to=None)

    def test_creation_of_locks_per_taxyear(self):
        new_lock1_2020 = self.old_lock_2020.lock_and_create()
        new_lock1_2020.lock_and_create()

        new_lock1_2021 = self.old_lock_2021.lock_and_create()
        new_lock1_2021.lock_and_create()

        self.assertEquals(6, Lock.objects.count())
        self.assertEquals(3, self.taxyear2020.lock_set.count())
        self.assertEquals(3, self.taxyear2021.lock_set.count())

        # Iterate through all Locks in year 2020 and 2021
        for lockset in (self.taxyear2020.lock_set.all().order_by('interval_from'), self.taxyear2021.lock_set.all().order_by('interval_from')):
            for i in range(len(lockset)):

                if i == 0:
                    # validate that the first lock starts on the first day of the TaxYear
                    self.assertEquals(lockset[0].interval_from.year, lockset[0].taxyear.year)
                    self.assertEquals(lockset[0].interval_from.month, 1)
                    self.assertEquals(lockset[0].interval_from.day, 1)
                    self.assertEquals(lockset[0].interval_to, lockset[1].interval_from)
                elif i < len(lockset)-1:
                    # All Locks except the last one needs to be closed, and end where the next one starts
                    self.assertEquals(lockset[i].interval_to, lockset[i+1].interval_from)
                else:
                    # Last Lock needs to be open
                    self.assertEquals(None, lockset[i].interval_to)

    def test_adding_taxslips_to_taxyear(self):

        person = Person.objects.create()
        persontaxyear2020 = PersonTaxYear.objects.create(person=person, tax_year=self.taxyear2020)
        persontaxyear2021 = PersonTaxYear.objects.create(person=person, tax_year=self.taxyear2021)

        FinalSettlement.objects.create(person_tax_year=persontaxyear2020, lock=self.taxyear2020.get_active_lock())
        FinalSettlement.objects.create(person_tax_year=persontaxyear2020, lock=self.taxyear2020.get_active_lock())
        FinalSettlement.objects.create(person_tax_year=persontaxyear2020, lock=self.taxyear2020.get_active_lock())
        FinalSettlement.objects.create(person_tax_year=persontaxyear2021, lock=self.taxyear2021.get_active_lock())
        FinalSettlement.objects.create(person_tax_year=persontaxyear2021, lock=self.taxyear2021.get_active_lock())
        FinalSettlement.objects.create(person_tax_year=persontaxyear2021, lock=self.taxyear2021.get_active_lock())

        self.assertEquals(2, Lock.objects.count())

        self.assertEquals(3, self.old_lock_2020.finalsettlement_set.count())

        self.assertEquals(3, self.old_lock_2021.finalsettlement_set.count())
