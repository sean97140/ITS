# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0003_auto_20141219_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='found_by',
            field=models.ForeignKey(to='users.User', related_name='item_found_by2'),
            preserve_default=True,
        ),
    ]
