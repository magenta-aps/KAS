# Generated by Django 2.2.18 on 2021-06-09 07:49

from django.db import migrations, models

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
        ('kas', '0012_fix_policy_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpolicytaxyear',
            name='next_processing_date',
            field=models.DateField(blank=True, null=True, verbose_name='Næste behandlingsdato'),
        ),
        migrations.AddField(
            model_name='policytaxyear',
            name='next_processing_date',
            field=models.DateField(blank=True, null=True, verbose_name='Næste behandlingsdato'),
        ),
        migrations.AlterField(
            model_name='historicalpolicytaxyear',
            name='self_reported_amount',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Selvangivet beløb'),
        ),
        migrations.AlterField(
            model_name='policytaxyear',
            name='self_reported_amount',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Selvangivet beløb'),
        ),
        migrations.AlterField(
            model_name='taxyear',
            name='year_part',
            field=models.TextField(choices=[('selvangivelse', 'Selvangivelsesperiode'), ('ligning', 'Ligningsperiode'), ('genoptagelsesperiode', 'Genoptagelsesperiode')], default='selvangivelse'),
        ),
        migrations.AddField(
            model_name='historicalpersontaxyear',
            name='all_documents_and_notes_handled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='persontaxyear',
            name='all_documents_and_notes_handled',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(
            set_all_documents_and_notes_handled,
            unset_all_documents_and_notes_handled
        ),
        migrations.AddField(
            model_name='historicalpolicytaxyear',
            name='citizen_pay_override',
            field=models.BooleanField(default=False, verbose_name='Borgeren betaler selvom der foreligger aftale med pensionsselskab'),
        ),
        migrations.AddField(
            model_name='policytaxyear',
            name='citizen_pay_override',
            field=models.BooleanField(default=False, verbose_name='Borgeren betaler selvom der foreligger aftale med pensionsselskab'),
        ),
    ]
