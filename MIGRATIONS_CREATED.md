# Migrations Created for New Features

## Summary

All migrations have been created for the new high-impact features. These migrations need to be applied to the database.

## Migrations Created

### 1. Users App
- **`backend/users/migrations/0007_add_login_alerts.py`**
  - Creates `LoginAlertPreference` model
  - Fields: notify_new_login, notify_new_device, notify_new_location
  - Channel preferences: email_enabled, push_enabled, in_app_enabled

### 2. Orders App
- **`backend/orders/migrations/0010_add_order_drafts_and_presets.py`**
  - Creates `OrderDraft` model (saved drafts before submission)
  - Creates `OrderPreset` model (reusable order presets)
  - Includes all relationships and indexes

- **`backend/orders/migrations/0011_add_enhanced_revisions.py`**
  - Creates `RevisionRequest` model (structured revision requests)
  - Fields: severity, priority, timeline, structured changes
  - Status tracking and assignment

### 3. Writer Management App
- **`backend/writer_management/migrations/0015_add_capacity_feedback_portfolio.py`**
  - Creates `WriterCapacity` model (max orders, blackout dates, preferences)
  - Creates `EditorWorkload` model (workload caps for editors)
  - Creates `Feedback` model (structured feedback with ratings)
  - Creates `FeedbackHistory` model (aggregated feedback metrics)
  - Creates `WriterPortfolio` model (opt-in portfolios)
  - Creates `PortfolioSample` model (sample work pieces)

## To Apply Migrations

```bash
# Using Docker (recommended)
docker-compose exec web python manage.py migrate

# Or locally
cd backend
python manage.py migrate
```

## Migration Dependencies

All migrations properly reference their dependencies:
- Users migration depends on websites and users previous migrations
- Orders migrations depend on order_configs, pricing_configs, websites
- Writer management migration depends on order_configs, websites, orders

## Next Steps After Migrations

1. ✅ Migrations created
2. ⏳ Apply migrations to database
3. ⏳ Create serializers for all models
4. ⏳ Create ViewSets/APIs
5. ⏳ Create frontend components
6. ⏳ Integration and testing

## Notes

- All models use proper foreign key relationships
- Indexes are included for performance
- ManyToMany relationships are properly configured
- JSON fields are used for flexible data storage (changes_required, blackout_dates, etc.)

