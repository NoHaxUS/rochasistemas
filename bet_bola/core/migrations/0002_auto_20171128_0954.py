# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-28 11:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reward',
            name='who_rewarded',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.Seller'),
        ),
        migrations.AddField(
            model_name='payment',
            name='who_set_payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.Seller'),
        ),
        migrations.AddField(
            model_name='game',
            name='championship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_games', to='core.Championship'),
        ),
        migrations.AddField(
            model_name='cotation',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cotations', to='core.Game'),
        ),
        migrations.AddField(
            model_name='betticket',
            name='cotations',
            field=models.ManyToManyField(related_name='my_bet_tickets', to='core.Cotation'),
        ),
        migrations.AddField(
            model_name='betticket',
            name='payment',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.Payment'),
        ),
        migrations.AddField(
            model_name='betticket',
            name='punter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_bet_tickets', to='user.Punter'),
        ),
        migrations.AddField(
            model_name='betticket',
            name='reward',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.Reward'),
        ),
        migrations.AddField(
            model_name='betticket',
            name='seller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bet_tickets_validated_by_me', to='user.Seller'),
        ),
    ]
