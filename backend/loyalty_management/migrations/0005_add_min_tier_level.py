# Generated manually to add min_tier_level field
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty_management', '0004_add_redemptionitem_missing_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='loyalty_management_redemptionitem' AND column_name='min_tier_level_id') THEN
                            ALTER TABLE loyalty_management_redemptionitem 
                            ADD COLUMN min_tier_level_id BIGINT REFERENCES loyalty_management_loyaltytier(id) ON DELETE SET NULL;
                        END IF;
                    END $$;
                """, reverse_sql=migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='redemptionitem',
                    name='min_tier_level',
                    field=models.ForeignKey(
                        blank=True,
                        help_text='Minimum loyalty tier required to redeem',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='redemption_items_requiring_tier',
                        to='loyalty_management.loyaltytier'
                    ),
                ),
            ],
        ),
    ]

