# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('items', '0002_auto_20141215_1530'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={'ordering': ['-pk']},
        ),
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ['-pk']},
        ),
        migrations.AddField(
            model_name='item',
            name='found_by',
            field=models.ForeignKey(default=1, related_name='item_found_by', to='users.User'),
            preserve_default=False,
        ),
    ]
