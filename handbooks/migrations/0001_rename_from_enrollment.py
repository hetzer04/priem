# handbooks/migrations/0001_rename_from_enrollment.py

from django.db import migrations

# SQL-команды для переименования таблиц
# Прямой ход: переименовываем из enrollment_* в handbooks_*
RENAME_TO_HANDBOOKS = """
ALTER TABLE "enrollment_specialty" RENAME TO "handbooks_specialty";
ALTER TABLE "enrollment_qualification" RENAME TO "handbooks_qualification";
"""

# Обратный ход: переименовываем из handbooks_* обратно в enrollment_*
RENAME_TO_ENROLLMENT = """
ALTER TABLE "handbooks_specialty" RENAME TO "enrollment_specialty";
ALTER TABLE "handbooks_qualification" RENAME TO "enrollment_qualification";
"""

class Migration(migrations.Migration):

    # Эта миграция не зависит ни от чего, она первая
    dependencies = []

    # Вместо создания таблиц, мы выполняем SQL-запрос на переименование
    operations = [
        migrations.RunSQL(RENAME_TO_HANDBOOKS, RENAME_TO_ENROLLMENT),
    ]