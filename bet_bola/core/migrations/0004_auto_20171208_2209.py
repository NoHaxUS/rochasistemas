# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-09 01:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20171208_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotation',
            name='handicap',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cotation',
            name='total',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cotation',
            name='winning',
            field=models.BooleanField(default=False),
        ),
    ]