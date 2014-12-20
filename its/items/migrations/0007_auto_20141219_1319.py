# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0006_auto_20141219_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='found_by',
            field=models.ForeignKey(to='users.User', related_name='item_found_by', default=1),
            preserve_default=False,
        ),
    ]
