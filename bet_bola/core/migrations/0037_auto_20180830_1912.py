# Generated by Django 2.1 on 2018-08-30 19:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20180711_1156'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ('-pk',), 'verbose_name': 'Jogo', 'verbose_name_plural': 'Jogos'},
        ),
    ]
