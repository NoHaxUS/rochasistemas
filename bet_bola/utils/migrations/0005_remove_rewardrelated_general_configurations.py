# Generated by Django 2.0.6 on 2018-10-26 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0004_auto_20181026_1007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rewardrelated',
            name='general_configurations',
        ),
    ]