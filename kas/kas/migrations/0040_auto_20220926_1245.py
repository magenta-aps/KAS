# Generated by Django 3.2.12 on 2022-09-26 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0039_test_persons'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalpolicytaxyear',
            old_name='adjusted_r75_amount',
            new_name='prefilled_amount_edited'
        ),
        migrations.RenameField(
            model_name='policytaxyear',
            old_name='adjusted_r75_amount',
            new_name='prefilled_amount_edited'
        ),
    ]
