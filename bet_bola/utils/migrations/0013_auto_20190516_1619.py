# Generated by Django 2.2.1 on 2019-05-16 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0012_auto_20190501_1441'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='generalconfigurations',
            options={'ordering': ['-pk'], 'verbose_name': 'Configurações Gerais', 'verbose_name_plural': 'Configurações Gerais'},
        ),
    ]
