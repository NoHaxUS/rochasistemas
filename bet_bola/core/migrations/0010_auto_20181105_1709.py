# Generated by Django 2.1.3 on 2018-11-05 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20181105_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='period',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='reward',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
