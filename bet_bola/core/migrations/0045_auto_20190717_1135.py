# Generated by Django 2.2.3 on 2019-07-17 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20190716_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaguemodified',
            name='priority',
            field=models.IntegerField(default=1, verbose_name='Prioridade'),
        ),
    ]
