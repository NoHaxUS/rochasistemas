# Generated by Django 2.1.3 on 2019-02-06 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_manager_can_change_limit_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manager',
            name='can_change_limit_time',
            field=models.BooleanField(default=False, verbose_name='Pode alterar tempo de Cancelamento do Cambista?'),
        ),
    ]
