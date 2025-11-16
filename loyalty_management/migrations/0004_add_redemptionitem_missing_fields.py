# Generated manually to add missing RedemptionItem fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty_management', '0003_alter_clientbadge_unique_together_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='loyalty_management_redemptionitem' AND column_name='total_redemptions') THEN
                            ALTER TABLE loyalty_management_redemptionitem ADD COLUMN total_redemptions INTEGER DEFAULT 0;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='loyalty_management_redemptionitem' AND column_name='max_per_client') THEN
                            ALTER TABLE loyalty_management_redemptionitem ADD COLUMN max_per_client INTEGER DEFAULT 1;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name='loyalty_management_redemptionitem' AND column_name='image_url') THEN
                            ALTER TABLE loyalty_management_redemptionitem ADD COLUMN image_url VARCHAR(200);
                        END IF;
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
                    name='total_redemptions',
                    field=models.PositiveIntegerField(default=0, help_text='Total number of times this item has been redeemed'),
                ),
                migrations.AddField(
                    model_name='redemptionitem',
                    name='max_per_client',
                    field=models.PositiveIntegerField(default=1, help_text='Maximum times a single client can redeem this item'),
                ),
                migrations.AddField(
                    model_name='redemptionitem',
                    name='image_url',
                    field=models.URLField(blank=True, help_text='Image URL for the redemption item', null=True),
                ),
                migrations.AddField(
                    model_name='redemptionitem',
                    name='min_tier_level',
                    field=models.ForeignKey(
                        blank=True,
                        help_text='Minimum loyalty tier required to redeem',
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name='redemption_items_requiring_tier',
                        to='loyalty_management.loyaltytier'
                    ),
                ),
            ],
        ),
    ]

