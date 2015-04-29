# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0014_auto_20150305_1149'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='category',
            name='machine_name',
            field=models.CharField(null=True, max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='is_valuable',
            field=models.BooleanField(help_text='Select this box if the item is an ID, key(s), or is valued at $50 or more. Items valued over $50 are turned into CPSO as soon as possible. Student IDs are turned in the ID services window in the Neuberger Hall Lobby. Checking this box automatically generates an email for the item to be picked up from the lab. USB DRIVES ARE NOT VALUABLE.', default=False),
            preserve_default=True,
        ),
    ]
