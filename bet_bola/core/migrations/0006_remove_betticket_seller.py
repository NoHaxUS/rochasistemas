# Generated by Django 2.0.1 on 2018-01-19 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20180114_2138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='betticket',
            name='seller',
        ),
    ]
