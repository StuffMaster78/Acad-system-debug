# Database Migration Guide - Tip Model

## Status

✅ **Tip model exported** in `writer_management/models/__init__.py`

## Migration Steps

### 1. Create Migration

When database is accessible (in Docker environment), run:

```bash
python manage.py makemigrations writer_management
```

This will create a migration file for the Tip model with all the new fields:
- `tip_type` (CharField with choices)
- `related_entity_type` (CharField, nullable)
- `related_entity_id` (PositiveIntegerField, nullable)
- `writer_percentage` (DecimalField)
- `payment` (ForeignKey to OrderPayment, nullable)
- `payment_status` (CharField with choices)
- `origin` (CharField)
- Database indexes for efficient querying

### 2. Review Migration

Check the generated migration file:
```bash
# The migration will be in:
writer_management/migrations/XXXX_add_tip_fields.py
```

Review the migration to ensure:
- All fields are included
- Indexes are created
- Foreign keys are properly set up
- Default values are correct

### 3. Apply Migration

```bash
python manage.py migrate writer_management
```

### 4. Verify Migration

After migration, verify the Tip table exists:
```bash
python manage.py dbshell
```

Then in PostgreSQL:
```sql
\d writer_management_tip
```

Or check via Django:
```python
python manage.py shell
>>> from writer_management.models.tipping import Tip
>>> Tip._meta.db_table
'writer_management_tip'
>>> Tip._meta.get_fields()
```

## Expected Migration Operations

The migration should include:

1. **CreateModel** for `Tip` (if table doesn't exist)
   OR
2. **AddField** operations for new fields (if table exists but fields are missing)

### Fields to be Added/Created:

- `tip_type` - CharField(max_length=20, choices=[...], default='direct')
- `related_entity_type` - CharField(max_length=50, null=True, blank=True)
- `related_entity_id` - PositiveIntegerField(null=True, blank=True)
- `writer_percentage` - DecimalField(max_digits=5, decimal_places=2)
- `payment` - ForeignKey to OrderPayment (null=True, blank=True)
- `payment_status` - CharField(max_length=20, choices=[...], default='pending')
- `origin` - CharField(max_length=50, default='client')

### Indexes to be Created:

- Index on `['client', 'website']`
- Index on `['writer', 'website']`
- Index on `['tip_type', 'related_entity_type', 'related_entity_id']`

## Rollback Plan

If migration needs to be rolled back:

```bash
python manage.py migrate writer_management XXXX
```

Where `XXXX` is the previous migration number.

## Notes

- The Tip model is now exported in `models/__init__.py`
- Migration should be created automatically when `makemigrations` is run
- All existing Tip records (if any) will need default values for new fields
- The `payment_status` field has a default of 'pending', so existing tips will be marked as pending

## Next Steps After Migration

1. ✅ Migration created
2. ✅ Migration applied
3. Test Tip creation via API
4. Test Admin Tip Management dashboard
5. Verify data integrity

