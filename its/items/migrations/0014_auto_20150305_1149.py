# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0013_auto_20150203_1226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='is_active',
        ),
        migrations.AddField(
            model_name='item',
            name='is_archived',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
