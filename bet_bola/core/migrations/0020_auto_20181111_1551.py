# Generated by Django 2.1.3 on 2018-11-11 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20181111_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotationhistory',
            name='original_cotation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history_cotation', to='core.Cotation', verbose_name='Cotação Original'),
        ),
    ]
