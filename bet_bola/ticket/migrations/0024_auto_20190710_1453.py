# Generated by Django 2.2.3 on 2019-07-10 14:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0023_merge_20190625_1502'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ('-pk',), 'verbose_name': 'Pagamento', 'verbose_name_plural': 'Pagamentos'},
        ),
        migrations.AlterModelOptions(
            name='reward',
            options={'ordering': ('-pk',), 'verbose_name': 'Recompensa', 'verbose_name_plural': 'Recompensas'},
        ),
    ]