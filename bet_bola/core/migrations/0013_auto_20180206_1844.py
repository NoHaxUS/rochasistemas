# Generated by Django 2.0.1 on 2018-02-06 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_remove_cotation_handicap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='ft_score',
            field=models.CharField(help_text='Placar final Ex: 3-5 (Casa-Visita)', max_length=80, null=True, verbose_name='Placar no final do Jogo'),
        ),
    ]