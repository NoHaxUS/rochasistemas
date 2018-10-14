# Generated by Django 2.1 on 2018-09-30 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_remove_betticket_cotation_value_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='betticket',
            name='bet_ticket_status',
            field=models.CharField(choices=[('Aguardando Resultados', 'Aguardando Resultados'), ('Não Venceu', 'Não Venceu'), ('Venceu', 'Venceu'), ('Venceu e não foi pago', 'Venceu e não foi pago'), ('Cancelado', 'Cancelado')], default='Aguardando Resultados', max_length=80, verbose_name='Status de Ticket'),
        ),
        migrations.AlterField(
            model_name='reward',
            name='status_reward',
            field=models.CharField(choices=[('Aguardando Resultados', 'Aguardando Resultados'), ('O apostador foi pago', 'O apostador foi pago'), ('Esse ticket não venceu', 'Esse ticket não venceu'), ('Venceu, Pagar Apostador', 'Venceu, Pagar Apostador'), ('Venceu e não foi pago', 'Venceu e não foi pago')], default='Aguardando Resultados', max_length=80, verbose_name='Status do Prêmio'),
        ),
    ]
