# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# -- View: last_status
class Migration(migrations.Migration):

    dependencies = [
        ('items', '0016_remove_item_possible_owner_contacted'),
    ]

    operations = [
        migrations.RunSQL("""

DROP VIEW IF EXISTS last_status;

CREATE OR REPLACE VIEW last_status AS 
 SELECT status.status_id,
    item.item_id,
    action.machine_name
   FROM item
     JOIN status USING (item_id)
     JOIN ( SELECT max(status_1.status_id) AS status_id
           FROM status status_1
          GROUP BY status_1.item_id) k USING (status_id)
     JOIN action ON status.action_taken_id = action.action_id;
""")
    ]