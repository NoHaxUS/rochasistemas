# Generated by Django 2.1.3 on 2018-11-05 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20181104_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
