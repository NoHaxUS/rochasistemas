# Generated by Django 2.1.3 on 2018-11-22 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0023_auto_20181122_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketremotion',
            name='market_to_remove',
            field=models.IntegerField(choices=[(2, 'Abaixo/Acima'), (21, 'Abaixo/Acima 1° Tempo'), (45, 'Abaixo/Acima 2° Tempo'), (101, 'Abaixo/Acima - Time de Casa'), (102, 'Abaixo/Acima - Time de Fora')], verbose_name='Tipo de Aposta'),
        ),
    ]