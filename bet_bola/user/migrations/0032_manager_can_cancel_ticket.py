# Generated by Django 2.0.6 on 2018-06-18 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0031_auto_20180615_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='manager',
            name='can_cancel_ticket',
            field=models.BooleanField(default=True),
        ),
    ]
