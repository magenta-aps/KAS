from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kas', '0010_auto_20210519_1209')
    ]

    operations = [
        migrations.RenameField(
            model_name='persontaxyear',
            old_name='general_notes',
            new_name='temporary_notes_field'
        ),
        migrations.RenameField(
            model_name='persontaxyear',
            old_name='foreign_pension_notes',
            new_name='general_notes'
        ),
        migrations.RenameField(
            model_name='persontaxyear',
            old_name='temporary_notes_field',
            new_name='foreign_pension_notes'
        ),
        migrations.RenameField(
            model_name='historicalpersontaxyear',
            old_name='general_notes',
            new_name='temporary_notes_field'
        ),
        migrations.RenameField(
            model_name='historicalpersontaxyear',
            old_name='foreign_pension_notes',
            new_name='general_notes'
        ),
        migrations.RenameField(
            model_name='historicalpersontaxyear',
            old_name='temporary_notes_field',
            new_name='foreign_pension_notes'
        ),
        migrations.AlterField(
            model_name='persontaxyear',
            name='foreign_pension_notes',
            field=models.TextField(null=True, verbose_name='Noter om pension i udlandet'),
        ),
        migrations.AlterField(
            model_name='persontaxyear',
            name='general_notes',
            field=models.TextField(null=True, verbose_name='Yderligere noter'),
        ),
        migrations.AlterField(
            model_name='historicalpersontaxyear',
            name='foreign_pension_notes',
            field=models.TextField(null=True, verbose_name='Noter om pension i udlandet'),
        ),
        migrations.AlterField(
            model_name='historicalpersontaxyear',
            name='general_notes',
            field=models.TextField(null=True, verbose_name='Yderligere noter'),
        ),
    ]
