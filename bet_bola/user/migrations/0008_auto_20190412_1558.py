# Generated by Django 2.1.7 on 2019-04-12 15:58

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20190404_1623'),
        ('user', '0007_normaluser_my_store'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_admin', models.BooleanField(default=False)),
                ('my_store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Store', verbose_name='Banca')),
            ],
            options={
                'verbose_name': 'Administrador',
                'verbose_name_plural': 'Administrador',
                'permissions': (('be_admin', 'Be a admin, permission.'),),
            },
            bases=('user.customuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='normaluser',
            name='my_store',
        ),
    ]
