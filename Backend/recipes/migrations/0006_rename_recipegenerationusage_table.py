from django.db import migrations


class Migration(migrations.Migration):
    """
    Rename the physical DB table from users_recipegenerationusage to
    recipes_recipegenerationusage now that the model lives in the recipes app.
    Migration 0005 moved the Django state but left the table name unchanged.
    """

    dependencies = [
        ('recipes', '0005_move_recipegenerationusage'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[],  # State already reflects recipes_recipegenerationusage
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE users_recipegenerationusage RENAME TO recipes_recipegenerationusage',
                    reverse_sql='ALTER TABLE recipes_recipegenerationusage RENAME TO users_recipegenerationusage',
                ),
            ],
        ),
    ]
