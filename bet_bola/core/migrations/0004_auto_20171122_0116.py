# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-22 03:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20171120_1003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotation',
            name='status',
            field=models.CharField(choices=[('OPEN', 'Resultado em Aberto'), ('NOT_HAPPENED', 'Não aconteceu'), ('HAPPENED', 'Aconteceu')], default='Resultado em Aberto', max_length=25),
        ),
        migrations.AlterField(
            model_name='game',
            name='status_game',
            field=models.CharField(choices=[('NS', 'Not Started'), ('LIVE', 'Live'), ('HT', 'Half-time'), ('FT', 'Full-Time'), ('ET', 'Extra-Time'), ('PEN_LIVE', 'Penalty Shootout'), ('AET', 'Finished after extra time'), ('BREAK', 'Match finished, waiting for extra time to start'), ('FT_PEN', 'Full-Time after penalties'), ('CANCL', 'Cancelled'), ('POSTP', 'PostPhoned'), ('INT', 'Interrupted'), ('ABAN', 'Abandoned'), ('SUSP', 'Suspended'), ('AWARDED', 'Awarded'), ('DELAYED', 'Delayed'), ('TBA', 'To Be Announced (Fixture will be updated with exact time later)'), ('WO', 'Walkover (Awarding of a victory to a contestant because there are no other contestants)')], default='Not Started', max_length=45),
        ),
    ]
