# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-25 13:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_remove_game_have_it'),
    ]

    operations = [
        migrations.AddField(
            model_name='championship',
            name='country',
            field=models.CharField(default=1, max_length=45),
            preserve_default=False,
        ),
    ]
