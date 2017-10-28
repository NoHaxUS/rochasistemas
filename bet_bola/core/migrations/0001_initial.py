# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-28 20:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
            ],
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=4)),
                ('reward_date', models.DateTimeField(null=True)),
            ],
        ),
    ]
