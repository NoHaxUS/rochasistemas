# Generated by Django 2.1.7 on 2019-03-27 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0006_auto_20190325_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalconfigurations',
            name='max_number_of_choices_per_bet',
            field=models.IntegerField(default=1, verbose_name='Número máximo de escolhas por Aposta'),
        ),
    ]