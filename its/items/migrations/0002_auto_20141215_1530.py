# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='possible_owner',
            field=models.ForeignKey(related_name='item_possible_owner', null=True, to='users.User'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='returned_to',
            field=models.ForeignKey(related_name='item_returned_to', null=True, to='users.User'),
            preserve_default=True,
        ),
    ]
