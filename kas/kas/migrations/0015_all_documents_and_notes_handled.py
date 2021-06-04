# Generated by Django 2.2.18 on 2021-06-02 12:14

from django.db import migrations


def set_all_documents_and_notes_handled(apps, schema_editor):
    PersonTaxYear = apps.get_model('kas', 'PersonTaxYear')
    for person in PersonTaxYear.objects.all():
        if person.policydocument_set.exists() or person.notes.exists():
            person.all_documents_and_notes_handled = False
            person.save(update_fields=['all_documents_and_notes_handled'])


def unset_all_documents_and_notes_handled(apps, schema_editor):
    PersonTaxYear = apps.get_model('kas', 'PersonTaxYear')
    for person in PersonTaxYear.objects.all():
        if person.policydocument_set.exists() or person.notes.exists():
            person.all_documents_and_notes_handled = True
            person.save(update_fields=['all_documents_and_notes_handled'])


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0014_auto_20210528_1501'),
    ]

    operations = [
        migrations.RunPython(set_all_documents_and_notes_handled, unset_all_documents_and_notes_handled),
    ]
