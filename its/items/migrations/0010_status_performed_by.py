# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('items', '0009_auto_20141222_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='performed_by',
            field=models.ForeignKey(null=True, default=None, to='users.User'),
            preserve_default=True,
        ),
    ]
