# Generated by Django 2.1.8 on 2019-04-09 17:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('icat_hooks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hookuser',
            name='DID',
        ),
        migrations.RemoveField(
            model_name='hookuser',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='hookuser',
            name='verkey',
        ),
        migrations.AddField(
            model_name='hookuser',
            name='user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
