import os
import uuid

from django.conf import settings
from django.db import migrations


def pensioncompanysummaryfile_file_path_old(instance, filename):
    now = instance.uploaded_at
    return (
        f"pensioncompany_summary/{instance.company.id}/"
        f"{instance.tax_year.year}/{now.strftime('%Y-%m-%d %H.%M.%S UTC')}.csv"
    )


def pensioncompanysummaryfile_file_path_new(instance, filename):
    return f"pensioncompany_summary/{instance.tax_year.year}/{uuid.uuid4()}.csv"


def policydocument_file_path_old(instance, filename):
    return filename


def policydocument_file_path_new(instance, filename):
    return f"policydocuments/{instance.person_tax_year.tax_year.year}/{uuid.uuid4()}"


def taxslipgenerated_file_path_old(instance, filename):
    return "reports/{filename}".format(filename=filename)


def taxslipgenerated_file_path_new(instance, filename):
    return f"taxslip/{instance.persontaxyear.tax_year.year}/{uuid.uuid4()}"


def finalsettlement_file_path_old(instance, filename):
    return "settlements/{year}/{uuid}.pdf".format(
        year=instance.person_tax_year.tax_year.year, uuid=instance.uuid.hex
    )


def finalsettlement_file_path_new(instance, filename):
    return f"settlements/{instance.person_tax_year.tax_year.year}/{uuid.uuid4()}.pdf"


def prepaymentfile_file_path_old(instance, filename):
    now = instance.uploaded_at
    return "pre_payments/{year}/{pk}".format(year=now.year, pk=instance.pk)


def prepaymentfile_file_path_new(instance, filename):
    now = instance.uploaded_at
    return f"pre_payments/{now.year}/{uuid.uuid4()}.csv"


def move_files(model, field, path_method):
    for item in model.objects.all():
        filefield = getattr(item, field, None)
        if (
            filefield is not None
            and filefield.name is not None
            and filefield.name != ""
        ):
            origin_full_path = os.path.join(settings.MEDIA_ROOT, filefield.name)
            dest_path = path_method(item, os.path.basename(origin_full_path))
            dest_full_path = os.path.join(settings.MEDIA_ROOT, dest_path)
            dest_full_path_dir = os.path.dirname(dest_full_path)
            if not os.path.exists(dest_full_path_dir):
                os.makedirs(dest_full_path_dir)

            if os.path.exists(origin_full_path):
                os.rename(origin_full_path, dest_full_path)
                print(f"Move file from {origin_full_path} to {dest_full_path}")
            elif os.path.exists(dest_full_path):
                print(f"File already exists at destination {dest_full_path}")
            else:
                print(
                    f"Would move file from {origin_full_path} to {dest_full_path}, but origin doesn't exist"
                )
            filefield.name = dest_path
            item.save()


def apply_migration(apps, schema_editor):
    for model, field, path_method in (
        (
            apps.get_model("kas", "PensionCompanySummaryFile"),
            "file",
            pensioncompanysummaryfile_file_path_new,
        ),
        (apps.get_model("kas", "PolicyDocument"), "file", policydocument_file_path_new),
        (
            apps.get_model("kas", "TaxSlipGenerated"),
            "file",
            taxslipgenerated_file_path_new,
        ),
        (
            apps.get_model("kas", "FinalSettlement"),
            "pdf",
            finalsettlement_file_path_new,
        ),
        (
            apps.get_model("prisme", "PrePaymentFile"),
            "file",
            prepaymentfile_file_path_new,
        ),
    ):
        move_files(model, field, path_method)
    remove_empty_folders(settings.MEDIA_ROOT, True)


def revert_migration(apps, schema_editor):
    for model, field, path_method in (
        (
            apps.get_model("kas", "PensionCompanySummaryFile"),
            "file",
            pensioncompanysummaryfile_file_path_old,
        ),
        (apps.get_model("kas", "PolicyDocument"), "file", policydocument_file_path_old),
        (
            apps.get_model("kas", "TaxSlipGenerated"),
            "file",
            taxslipgenerated_file_path_old,
        ),
        (
            apps.get_model("kas", "FinalSettlement"),
            "pdf",
            finalsettlement_file_path_old,
        ),
        (
            apps.get_model("prisme", "PrePaymentFile"),
            "file",
            prepaymentfile_file_path_old,
        ),
    ):
        move_files(model, field, path_method)
    remove_empty_folders(settings.MEDIA_ROOT, True)


def remove_empty_folders(path, toplevel=False):
    # Depth-first folder removal - empty folders are removed, and if their parents become empty, remove them too
    if os.path.isdir(path):
        entries = [os.path.join(path, item) for item in os.listdir(path)]
        if entries:
            for entry in entries:
                remove_empty_folders(entry)
            entries = [os.path.join(path, item) for item in os.listdir(path)]
        if not entries and not toplevel:
            os.rmdir(path)


class Migration(migrations.Migration):

    dependencies = [
        ("kas", "0029_auto_20220328_0920"),
        ("prisme", "0008_auto_20220316_1521"),
        ("kas", "0030_auto_20220426_0852"),
    ]

    operations = [migrations.RunPython(apply_migration, reverse_code=revert_migration)]
