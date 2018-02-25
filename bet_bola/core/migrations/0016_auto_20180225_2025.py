# Generated by Django 2.0.1 on 2018-02-25 20:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20180219_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Tipo de Aposta')),
            ],
            options={
                'verbose_name': 'Tipo de Aposta',
                'verbose_name_plural': 'Tipo de Aposta',
            },
        ),
        migrations.AlterField(
            model_name='betticket',
            name='payment',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Payment', verbose_name='Pagamento'),
        ),
        migrations.AlterField(
            model_name='betticket',
            name='reward',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Reward', verbose_name='Recompensa'),
        ),
        migrations.AlterField(
            model_name='betticket',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='my_bet_tickets', to=settings.AUTH_USER_MODEL, verbose_name='Apostador'),
        ),
        migrations.AlterField(
            model_name='betticket',
            name='value',
            field=models.FloatField(verbose_name='Valor Apostado'),
        ),
        migrations.AlterField(
            model_name='championship',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='my_championships', to='core.Country', verbose_name='Pais'),
        ),
        migrations.AlterField(
            model_name='cotation',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cotations', to='core.Game', verbose_name='Jogo'),
        ),
        migrations.AlterField(
            model_name='cotation',
            name='kind',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cotations', to='core.Market', verbose_name='Jogo'),
        ),
        migrations.AlterField(
            model_name='game',
            name='championship',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='my_games', to='core.Championship', verbose_name='Campeonato'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='who_set_payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.Seller'),
        ),
        migrations.AlterField(
            model_name='reward',
            name='who_rewarded',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.Seller'),
        ),
    ]
