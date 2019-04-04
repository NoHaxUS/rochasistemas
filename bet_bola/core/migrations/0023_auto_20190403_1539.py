# Generated by Django 2.1.7 on 2019-04-03 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_game_results_calculated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cotation',
            name='status',
        ),
        migrations.AlterField(
            model_name='cotation',
            name='settlement',
            field=models.IntegerField(choices=[(0, 'Em Aberto'), (-1, 'Cancelada'), (1, 'Perdeu'), (2, 'Ganhou')], default=0, verbose_name='Resultado'),
        ),
    ]