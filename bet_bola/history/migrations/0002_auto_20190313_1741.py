# Generated by Django 2.1.3 on 2019-03-13 17:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190313_1741'),
        ('ticket', '0002_auto_20190313_1741'),
        ('user', '0002_auto_20190313_1741'),
        ('history', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='managertransactions',
            name='manager',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.Manager', verbose_name='Gerente'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='managertransactions',
            name='seller',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.Seller', verbose_name='Cambista'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='managertransactions',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Store', verbose_name='Banca'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='punterpayedhistory',
            name='seller',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.Seller', verbose_name='Cambista'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='punterpayedhistory',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Store', verbose_name='Banca'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='punterpayedhistory',
            name='ticket_winner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ticket.Ticket', verbose_name='Bilhete Vencedor'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='revenuehistorymanager',
            name='manager',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.Manager', verbose_name='Gerente'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='revenuehistorymanager',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Store', verbose_name='Banca'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='revenuehistoryseller',
            name='seller',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.Seller', verbose_name='Cambista'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='revenuehistoryseller',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Store', verbose_name='Banca'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sellersaleshistory',
            name='bet_ticket',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ticket.Ticket', verbose_name='Bilhete Pago'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sellersaleshistory',
            name='seller',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.Seller', verbose_name='Cambista'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sellersaleshistory',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Store', verbose_name='Banca'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticketcancelationhistory',
            name='seller_of_payed',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.Seller', verbose_name='Cambista'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticketcancelationhistory',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Store', verbose_name='Banca'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticketcancelationhistory',
            name='ticket_cancelled',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ticket.Ticket', verbose_name='Bilhete Cancelado'),
            preserve_default=False,
        ),
    ]
