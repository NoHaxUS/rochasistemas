# Generated by Django 2.1.7 on 2019-03-18 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Última Atualização'),
        ),
    ]
