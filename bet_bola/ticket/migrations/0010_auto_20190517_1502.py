# Generated by Django 2.2.1 on 2019-05-17 15:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0009_remove_ticket_creator_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='who_paid_type',
        ),
        migrations.AlterField(
            model_name='reward',
            name='who_rewarded_the_winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
