# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-28 11:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BetTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('value', models.DecimalField(decimal_places=2, max_digits=4)),
                ('bet_ticket_status', models.CharField(choices=[('WAITING_RESULT', 'Aguardando Resultados'), ('NOT_WON', 'Não Ganhou'), ('WON', 'Ganhou')], default=('WAITING_RESULT', 'Aguardando Resultados'), max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Championship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Cotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75)),
                ('value', models.FloatField()),
                ('winning', models.BooleanField(default=False)),
                ('is_standard', models.BooleanField(default=False)),
                ('kind', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('start_game_date', models.DateTimeField()),
                ('status_game', models.CharField(choices=[('NS', 'Not Started'), ('LIVE', 'Live'), ('HT', 'Half-time'), ('FT', 'Full-Time'), ('ET', 'Extra-Time'), ('PEN_LIVE', 'Penalty Shootout'), ('AET', 'Finished after extra time'), ('BREAK', 'Match finished, waiting for extra time to start'), ('FT_PEN', 'Full-Time after penalties'), ('CANCL', 'Cancelled'), ('POSTP', 'PostPhoned'), ('INT', 'Interrupted'), ('ABAN', 'Abandoned'), ('SUSP', 'Suspended'), ('AWARDED', 'Awarded'), ('DELAYED', 'Delayed'), ('TBA', 'To Be Announced (Fixture will be updated with exact time later)'), ('WO', 'Walkover (Awarding of a victory to a contestant because there are no other contestants)')], default='NS', max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_payment', models.CharField(choices=[('PAID', 'Pago'), ('WATING_PAYMENT', 'Aguardando Pagamento do Ticket')], max_length=25)),
                ('payment_date', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reward_date', models.DateTimeField(null=True)),
                ('value', models.DecimalField(decimal_places=2, max_digits=6)),
                ('status_reward', models.CharField(choices=[('PAID', 'O apostador foi pago'), ('NOT_PAID', 'O apostador ainda não foi pago'), ('NOT_WON', 'Esse ticket não venceu')], max_length=25)),
            ],
        ),
    ]
