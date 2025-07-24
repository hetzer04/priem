# orders/migrations/0001_rename_from_enrollment.py
from django.db import migrations

RENAME_TO_ORDERS = 'ALTER TABLE "enrollment_order" RENAME TO "orders_order";'
RENAME_TO_ENROLLMENT = 'ALTER TABLE "orders_order" RENAME TO "enrollment_order";'

# Также нужно переименовать таблицу для связи ManyToMany с абитуриентами
RENAME_M2M_TO_ORDERS = 'ALTER TABLE "enrollment_order_applicants" RENAME TO "orders_order_applicants";'
RENAME_M2M_TO_ENROLLMENT = 'ALTER TABLE "orders_order_applicants" RENAME TO "enrollment_order_applicants";'

class Migration(migrations.Migration):
    dependencies = []
    operations = [
        migrations.RunSQL(RENAME_TO_ORDERS, RENAME_TO_ENROLLMENT),
        migrations.RunSQL(RENAME_M2M_TO_ORDERS, RENAME_M2M_TO_ENROLLMENT),
    ]