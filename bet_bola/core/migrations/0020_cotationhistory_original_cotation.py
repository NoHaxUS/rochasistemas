# Generated by Django 2.0.1 on 2018-05-13 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_cotationhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotationhistory',
            name='original_cotation',
            field=models.IntegerField(default=9999),
            preserve_default=False,
        ),
    ]
