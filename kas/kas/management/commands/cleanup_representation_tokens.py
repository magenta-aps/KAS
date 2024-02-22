from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from kas.models import RepresentationToken


class Command(BaseCommand):
    help = "Removes obsolete RepresentationTokens"

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(
            seconds=settings.SELVBETJENING_REPRESENTATION_TOKEN_MAX_AGE
        )
        RepresentationToken.objects.filter(created__lt=cutoff).delete()
