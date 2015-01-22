# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0010_status_performed_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='found_by',
        ),
    ]
