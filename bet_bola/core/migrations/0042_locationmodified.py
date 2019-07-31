# Generated by Django 2.2.3 on 2019-07-15 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_leaguemodified_available'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationModified',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(default=1, verbose_name='Prioridade')),
                ('available', models.BooleanField(default=True, verbose_name='Visível?')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_modifications', to='core.Location', verbose_name='Liga Alterada')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_locations_modifications', to='core.Store', verbose_name='Banca')),
            ],
            options={
                'verbose_name': 'Liga Banca',
                'verbose_name_plural': 'Ligas da Banca',
                'ordering': ('-pk',),
            },
        ),
    ]