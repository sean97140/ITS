# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0012_auto_20150127_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('machine_name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'last_status',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
