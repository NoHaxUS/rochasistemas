# Generated by Django 2.1 on 2018-10-16 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20181016_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotation',
            name='line',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True),
        ),
        migrations.AlterField(
            model_name='cotation',
            name='settlement',
            field=models.IntegerField(blank=True, choices=[(-1, 'Cancelada'), (1, 'Perdeu'), (2, 'Ganhou'), (3, 'Reembolso'), (4, 'Metade Perdida'), (3, 'Metade Ganha')], null=True),
        ),
    ]
