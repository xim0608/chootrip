# Generated by Django 2.1.1 on 2018-09-18 08:34

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0003_analyzedreview_mecab_neologd'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyzedreview',
            name='jumanpp',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default=None, max_length=255), blank=True, size=None), blank=True, null=True, size=None),
        ),
    ]
