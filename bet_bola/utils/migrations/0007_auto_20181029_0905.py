# Generated by Django 2.0.6 on 2018-10-29 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0006_ticketcustommessage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticketcustommessage',
            options={'verbose_name': 'Mensagem a ser mostrada no ticket', 'verbose_name_plural': 'Mensagem a ser mostrada no ticket'},
        ),
        migrations.AlterField(
            model_name='ticketcustommessage',
            name='text',
            field=models.TextField(max_length=45, verbose_name='Mensagem customizada'),
        ),
    ]
