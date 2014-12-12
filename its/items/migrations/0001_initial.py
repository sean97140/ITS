# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('action_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'action',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'category',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('is_valuable', models.BooleanField(default=False)),
                ('possible_owner_contacted', models.BooleanField(default=False)),
                ('category', models.ForeignKey(to='items.Category')),
            ],
            options={
                'db_table': 'item',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('location_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'location',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('status_id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField()),
                ('action_taken', models.ForeignKey(to='items.Action')),
                ('item', models.ForeignKey(to='items.Item')),
            ],
            options={
                'db_table': 'status',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='location',
            field=models.ForeignKey(to='items.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='possible_owner',
            field=models.ForeignKey(to='users.User', related_name='item_possible_owner'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='returned_to',
            field=models.ForeignKey(to='users.User', related_name='item_returned_to'),
            preserve_default=True,
        ),
    ]
