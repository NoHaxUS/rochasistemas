# Generated by Django 2.0.6 on 2018-10-26 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RewardRelated',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_max', models.DecimalField(decimal_places=2, default=0, max_digits=30, verbose_name='Valor da Apostas')),
                ('reward_value_max', models.DecimalField(decimal_places=2, default=100000, max_digits=30, verbose_name='Valor Máximo da Recompensa')),
                ('general_configurations', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reward_related', to='utils.GeneralConfigurations')),
            ],
        ),
    ]