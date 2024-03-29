# Generated by Django 2.2.26 on 2022-02-10 08:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kas', '0022_auto_20220124_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressFromDafo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpr', models.TextField(null=False, unique=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('postal_area', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('co', models.TextField(blank=True, null=True)),
                ('full_address', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='historicalpersontaxyear',
            name='updated_from_dafo',
        ),
        migrations.RemoveField(
            model_name='persontaxyear',
            name='updated_from_dafo',
        ),
        migrations.AddField(
            model_name='historicalperson',
            name='updated_from_dafo',
            field=models.BooleanField(default=False, verbose_name='Opdateret fra datafordeleren'),
        ),
        migrations.AddField(
            model_name='historicalpersontaxyear',
            name='updated_by',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='historicalpolicytaxyear',
            name='updated_by',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='updated_from_dafo',
            field=models.BooleanField(default=False, verbose_name='Opdateret fra datafordeleren'),
        ),
        migrations.AddField(
            model_name='persontaxyear',
            name='updated_by',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='policytaxyear',
            name='updated_by',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.CreateModel(
            name='RepresentationToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=64, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('consumed', models.BooleanField(default=False)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kas.Person')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
