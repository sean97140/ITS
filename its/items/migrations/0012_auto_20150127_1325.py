# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0011_remove_item_found_by'),
    ]

    operations = [
        migrations.RunSQL("""
CREATE VIEW last_status AS
SELECT 
    *
FROM 
    item
INNER JOIN
    status USING(item_id)
INNER JOIN (
    SELECT 
        MAX(status_id) AS status_id
    FROM
        status
    GROUP BY item_id
) k USING(status_id)
INNER JOIN 
    "action" ON action_taken_id = action_id
""")
    ]
