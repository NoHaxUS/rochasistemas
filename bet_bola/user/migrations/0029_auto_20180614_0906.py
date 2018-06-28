# Generated by Django 2.0.6 on 2018-06-14 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0028_auto_20180613_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='manager',
            name='address',
            field=models.CharField(blank=True, max_length=75, null=True, verbose_name='Endereço'),
        ),
        migrations.AlterField(
            model_name='manager',
            name='cpf',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='CPF'),
        ),
    ]