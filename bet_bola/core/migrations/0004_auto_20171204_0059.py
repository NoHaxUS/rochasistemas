# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-04 02:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20171204_0028'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='betticket',
            options={'permissions': (('can_validate_payment', 'Can validate user ticket'), ('can_reward', 'Can reward a user'))},
        ),
    ]