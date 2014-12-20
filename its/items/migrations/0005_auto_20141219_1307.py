# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('items', '0004_auto_20141219_1306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='found_by',
        ),
        migrations.AddField(
            model_name='item',
            name='found_by_person',
            field=models.ForeignKey(to='users.User', related_name='item_found_by_person', null=True),
            preserve_default=True,
        ),
    ]
