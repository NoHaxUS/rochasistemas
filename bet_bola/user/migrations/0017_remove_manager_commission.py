# Generated by Django 2.2.1 on 2019-06-03 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_auto_20190523_1743'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manager',
            name='commission',
        ),
    ]