# Generated by Django 2.2.4 on 2019-08-14 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0045_auto_20190812_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='closed',
            field=models.BooleanField(default=False, verbose_name='Prestado conta?'),
        ),
    ]