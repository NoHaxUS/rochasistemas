# Generated by Django 2.2.3 on 2019-07-17 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0030_auto_20190717_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seller',
            name='limit_time_to_cancel',
            field=models.IntegerField(default=5, verbose_name='Tempo Limite de Cancelamento'),
        ),
    ]