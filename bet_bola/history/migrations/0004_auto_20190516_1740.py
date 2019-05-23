# Generated by Django 2.2.1 on 2019-05-16 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_auto_20190513_1634'),
        ('ticket', '0008_auto_20190516_1740'),
        ('history', '0003_auto_20190516_1700'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketValidationHistory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('who_validated', models.CharField(max_length=200, verbose_name='Quem Validou')),
                ('validation_date', models.DateTimeField(auto_now_add=True, verbose_name='Data da Venda')),
                ('bet_value', models.DecimalField(decimal_places=2, max_digits=30, verbose_name='Valor Apostado')),
                ('balance_before', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, verbose_name='Saldo Anterior')),
                ('balance_after', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, verbose_name='Saldo Atual')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Store', verbose_name='Banca')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticket.Ticket', verbose_name='Bilhete Validado')),
            ],
            options={
                'verbose_name': 'Validação de Aposta',
                'verbose_name_plural': 'Validações de Apostas',
                'ordering': ['-pk'],
            },
        ),
        migrations.DeleteModel(
            name='SellerSalesHistory',
        ),
    ]