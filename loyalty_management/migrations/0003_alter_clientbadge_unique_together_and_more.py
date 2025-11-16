# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty_management', '0002_initial'),
        ('client_management', '0002_initial'),
        ('websites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='clientbadge',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='clientbadge',
            name='website',
            field=models.ForeignKey(help_text='Website this badge is associated with', on_delete=django.db.models.deletion.CASCADE, related_name='client_badges', to='websites.website'),
        ),
        migrations.AlterUniqueTogether(
            name='clientbadge',
            unique_together={('client', 'badge_name')},
        ),
        migrations.CreateModel(
            name='RedemptionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Category name (e.g., 'Discounts', 'Products', 'Services')", max_length=100)),
                ('description', models.TextField(blank=True, help_text='Description of this redemption category', null=True)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this category is active for redemptions')),
                ('sort_order', models.PositiveIntegerField(default=0, help_text='Display order for categories')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemption_categories', to='websites.website')),
            ],
            options={
                'verbose_name': 'Redemption Category',
                'verbose_name_plural': 'Redemption Categories',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='RedemptionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Name of the redemption item (e.g., '$10 Discount', 'Free Writing Service')", max_length=200)),
                ('description', models.TextField(help_text='Detailed description of what the client receives')),
                ('points_required', models.PositiveIntegerField(help_text='Number of loyalty points required for redemption')),
                ('redemption_type', models.CharField(choices=[('discount', 'Discount Code'), ('cash', 'Cash/Wallet Credit'), ('product', 'Physical Product'), ('service', 'Service Credit'), ('voucher', 'Voucher/Code')], default='discount', help_text='Type of redemption item', max_length=20)),
                ('discount_code', models.CharField(blank=True, help_text='Discount code to generate/apply (for discount type)', max_length=50, null=True)),
                ('discount_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Discount amount in dollars (for discount/cash types)', max_digits=10, null=True)),
                ('discount_percentage', models.DecimalField(blank=True, decimal_places=2, help_text='Discount percentage (for discount type)', max_digits=5, null=True)),
                ('stock_quantity', models.PositiveIntegerField(blank=True, help_text='Available stock (null = unlimited)', null=True)),
                ('total_redemptions', models.PositiveIntegerField(default=0, help_text='Total number of times this item has been redeemed')),
                ('max_per_client', models.PositiveIntegerField(default=1, help_text='Maximum times a single client can redeem this item')),
                ('image_url', models.URLField(blank=True, help_text='Image URL for the redemption item', null=True)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this item is available for redemption')),
                ('sort_order', models.PositiveIntegerField(default=0, help_text='Display order')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(help_text='Category this redemption item belongs to', on_delete=django.db.models.deletion.PROTECT, related_name='items', to='loyalty_management.redemptioncategory')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemption_items', to='websites.website')),
            ],
            options={
                'verbose_name': 'Redemption Item',
                'verbose_name_plural': 'Redemption Items',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='RedemptionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points_used', models.PositiveIntegerField(help_text='Points deducted for this redemption')),
                ('status', models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('fulfilled', 'Fulfilled'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', help_text='Current status of the redemption request', max_length=20)),
                ('fulfillment_code', models.CharField(blank=True, help_text='Generated code/voucher for fulfillment (e.g., discount code)', max_length=100, null=True)),
                ('fulfillment_details', models.JSONField(blank=True, default=dict, help_text='Additional fulfillment details (e.g., tracking number, delivery address)')),
                ('rejection_reason', models.TextField(blank=True, help_text='Reason for rejection if applicable', null=True)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('fulfilled_at', models.DateTimeField(blank=True, null=True)),
                ('rejected_at', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, help_text='Admin who approved this redemption', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_redemptions', to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemption_requests', to='client_management.clientprofile')),
                ('fulfilled_by', models.ForeignKey(blank=True, help_text='Admin who fulfilled this redemption', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fulfilled_redemptions', to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='requests', to='loyalty_management.redemptionitem')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemption_requests', to='websites.website')),
            ],
            options={
                'verbose_name': 'Redemption Request',
                'verbose_name_plural': 'Redemption Requests',
                'ordering': ['-requested_at'],
            },
        ),
        migrations.CreateModel(
            name='LoyaltyAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('total_active_clients', models.PositiveIntegerField(default=0, help_text='Total clients with loyalty points')),
                ('total_points_issued', models.PositiveIntegerField(default=0, help_text='Total points issued in period')),
                ('total_points_redeemed', models.PositiveIntegerField(default=0, help_text='Total points redeemed in period')),
                ('total_points_balance', models.PositiveIntegerField(default=0, help_text='Total outstanding points balance')),
                ('total_redemptions', models.PositiveIntegerField(default=0, help_text='Total number of redemptions')),
                ('total_redemption_value', models.DecimalField(decimal_places=2, default=0.0, help_text='Total value of redemptions (in points)', max_digits=12)),
                ('bronze_count', models.PositiveIntegerField(default=0)),
                ('silver_count', models.PositiveIntegerField(default=0)),
                ('gold_count', models.PositiveIntegerField(default=0)),
                ('platinum_count', models.PositiveIntegerField(default=0)),
                ('active_redemptions_ratio', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of active clients who redeemed', max_digits=5)),
                ('average_points_per_client', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('calculated_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('most_popular_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='analytics_as_popular', to='loyalty_management.redemptionitem')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loyalty_analytics', to='websites.website')),
            ],
            options={
                'verbose_name': 'Loyalty Analytics',
                'verbose_name_plural': 'Loyalty Analytics',
                'ordering': ['-date_to', '-date_from'],
            },
        ),
        migrations.CreateModel(
            name='DashboardWidget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('widget_type', models.CharField(choices=[('points_issued', 'Points Issued Over Time'), ('redemptions_trend', 'Redemptions Trend'), ('tier_distribution', 'Loyalty Tier Distribution'), ('top_redemptions', 'Top Redemption Items'), ('engagement_rate', 'Client Engagement Rate'), ('points_balance', 'Total Points Balance'), ('conversion_rate', 'Points to Wallet Conversion')], max_length=50)),
                ('title', models.CharField(help_text='Custom title for the widget', max_length=200)),
                ('config', models.JSONField(blank=True, default=dict, help_text='Widget-specific configuration')),
                ('is_visible', models.BooleanField(default=True, help_text='Whether this widget is visible on the dashboard')),
                ('sort_order', models.PositiveIntegerField(default=0, help_text='Display order on dashboard')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_widgets', to='websites.website')),
            ],
            options={
                'verbose_name': 'Dashboard Widget',
                'verbose_name_plural': 'Dashboard Widgets',
                'ordering': ['sort_order', 'title'],
            },
        ),
        migrations.AddField(
            model_name='loyaltytransaction',
            name='redemption_request',
            field=models.ForeignKey(blank=True, help_text='Redemption request associated with this transaction (if applicable)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='loyalty_management.redemptionrequest'),
        ),
        migrations.AddConstraint(
            model_name='redemptioncategory',
            constraint=models.UniqueConstraint(fields=['website', 'name'], name='unique_category_per_website'),
        ),
        migrations.AddConstraint(
            model_name='loyaltyanalytics',
            constraint=models.UniqueConstraint(fields=['website', 'date_from', 'date_to'], name='unique_analytics_per_website_date_range'),
        ),
    ]


