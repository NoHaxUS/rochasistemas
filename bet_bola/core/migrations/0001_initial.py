# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-30 14:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='BetTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(null=True)),
                ('value', models.DecimalField(decimal_places=2, max_digits=4)),
                ('bet_ticket_status', models.CharField(choices=[('WAITING_RESULT', 'waiting result'), ('NOT_WON', 'not won'), ('WON', 'won')], max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Cotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('value', models.DecimalField(decimal_places=2, max_digits=4)),
                ('status', models.CharField(choices=[('OPEN', 'open'), ('HAPPEN', 'happen'), ('NOT_HAPPEN', 'not_happen')], max_length=25)),
                ('bet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cotations', to='core.Bet')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('start_game_date', models.DateTimeField(null=True)),
                ('championship', models.CharField(max_length=25)),
                ('visible', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PAID', 'paid'), ('NOT_PAID', 'not_paid')], max_length=25)),
                ('payment_date', models.DateTimeField(null=True)),
                ('who_set_payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Seller')),
            ],
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=4)),
                ('reward_date', models.DateTimeField(null=True)),
                ('who_rewarded', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Seller')),
            ],
        ),
        migrations.AddField(
            model_name='cotation',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cotations', to='core.Game'),
        ),
        migrations.AddField(
            model_name='betticket',
            name='payment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Payment'),
        ),
        migrations.AddField(
            model_name='betticket',
            name='punter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_bet_tickets', to='user.Punter'),
        ),
        migrations.AddField(
            model_name='betticket',
            name='reward',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Reward'),
        ),
        migrations.AddField(
            model_name='betticket',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bet_tickets_validated_by_me', to='user.Seller'),
        ),
        migrations.AddField(
            model_name='bet',
            name='bet_ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_bets', to='core.BetTicket'),
        ),
        migrations.AddField(
            model_name='bet',
            name='cotation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_bets', to='core.Cotation'),
        ),
    ]
