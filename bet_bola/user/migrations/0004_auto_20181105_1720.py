# Generated by Django 2.1.3 on 2018-11-05 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20181105_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='punter',
            name='cellphone',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='Celular'),
        ),
    ]