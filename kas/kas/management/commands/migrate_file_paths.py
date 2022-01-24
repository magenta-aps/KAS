from django.core.management.base import BaseCommand
from django.conf import settings
from kas.models import PensionCompanySummaryFile, FinalSettlement, PolicyDocument, TaxSlipGenerated
from prisme.models import PrePaymentFile
import os


class Command(BaseCommand):
    help = 'Reorganizes files into their new paths'

    def handle(self, *args, **options):
        for model, field in (
            (PensionCompanySummaryFile, 'file'),
            (PolicyDocument, 'file'),
            (TaxSlipGenerated, 'file'),
            (FinalSettlement, 'pdf'),
            (PrePaymentFile, 'file'),
        ):
            for item in model.objects.all():
                try:
                    filefield = getattr(item, field)
                    old_path = filefield.path
                    new_path = item.file_path(os.path.basename(old_path))
                    new_full_path = f"{settings.MEDIA_ROOT}/{new_path}"
                    new_full_path_dir = os.path.dirname(new_full_path)
                    if not os.path.exists(new_full_path_dir):
                        os.makedirs(new_full_path_dir)
                    os.rename(old_path, new_full_path)
                    filefield.name = new_path
                    item.save()
                except ValueError:
                    # Some file fields don't actually have files, so don't explode over it
                    pass
        self.remove_empty_folders(settings.MEDIA_ROOT, True)

    def remove_empty_folders(self, path, toplevel=False):
        # Depth-first folder removal - empty folders are removed, and if their parents become empty, remove them too
        if os.path.isdir(path):
            entries = [os.path.join(path, item) for item in os.listdir(path)]
            if entries:
                for entry in entries:
                    self.remove_empty_folders(entry)
                entries = [os.path.join(path, item) for item in os.listdir(path)]
            if not entries and not toplevel:
                os.rmdir(path)
