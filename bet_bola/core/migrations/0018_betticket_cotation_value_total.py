# Generated by Django 2.0.1 on 2018-04-26 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20180225_2039'),
    ]

    operations = [
        migrations.AddField(
            model_name='betticket',
            name='cotation_value_total',
            field=models.FloatField(default=1, verbose_name='Cota Total da Aposta'),
            preserve_default=False,
        ),
    ]
