# Generated by Django 3.1.4 on 2021-11-13 12:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0007_auto_20211113_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bad_borrower',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2023, 10, 21, 12, 20, 20, 235484, tzinfo=utc), verbose_name='Date de fin'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2021, 12, 13, 12, 20, 20, 235484, tzinfo=utc), verbose_name='Date de fin'),
        ),
        migrations.AlterField(
            model_name='ouvrageinstance',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, help_text='Unique ID pour cette version dans toute la biliothèque', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='ending_date',
            field=models.DateField(default=datetime.datetime(2022, 11, 12, 12, 20, 20, 235484, tzinfo=utc), verbose_name='Date de fin'),
        ),
    ]