# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0008_auto_20141219_1624'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={'ordering': ['-weight']},
        ),
    ]
