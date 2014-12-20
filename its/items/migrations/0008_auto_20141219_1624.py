# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0007_auto_20141219_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='machine_name',
            field=models.CharField(unique=True, default='CHECKED_IN', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='action',
            name='weight',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
