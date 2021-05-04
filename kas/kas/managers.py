from django.db import models


class PolicyTaxYearManager(models.Manager):

    def active(self):
        return self.filter(active=True)
