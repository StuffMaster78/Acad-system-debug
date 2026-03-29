# Migration Status

## Current Situation

Django has detected model changes in multiple apps that need migrations. The migration `0009_add_invoice_indexes.py` for `order_payments_management` has been created manually and is ready.

## Migration File Created

✅ **order_payments_management/migrations/0009_add_invoice_indexes.py**
- Adds 8 new indexes to the Invoice model
- Dependencies: `0008_update_invoice_model_complete`
- Status: Ready to apply

## Next Steps

### Option 1: Apply Only Invoice Indexes Migration (Recommended)

If you only want to apply the invoice indexes migration we just created:

```bash
python3 manage.py migrate order_payments_management 0009_add_invoice_indexes
```

### Option 2: Check What Django Detects

To see what other changes Django has detected in other apps:

```bash
python3 manage.py makemigrations --dry-run
```

This will show you what migrations Django wants to create without actually creating them.

### Option 3: Create All Missing Migrations

If you want Django to create migrations for all detected changes:

```bash
python3 manage.py makemigrations
```

Then review the generated migration files before applying:

```bash
python3 manage.py migrate
```

## Invoice Indexes Migration Details

The migration `0009_add_invoice_indexes.py` adds the following indexes:

**Single Field Indexes:**
- `is_paid` - For filtering by payment status
- `created_at` - For date-based ordering
- `client` - For client-based filtering
- `website` - For multi-tenant filtering
- `due_date` - For due date filtering

**Composite Indexes:**
- `(client, is_paid)` - Client invoices by status
- `(website, created_at)` - Multi-tenant with date ordering
- `(is_paid, created_at)` - Status with date ordering

**Note:** Some indexes already exist from migration 0008:
- `reference_id` (already exists)
- `payment_token` (already exists)
- `(is_paid, due_date)` (already exists)
- `(website, is_paid)` (already exists)

## Verification

After applying migrations, verify indexes were created:

```sql
-- PostgreSQL
\d order_payments_management_invoice

-- Or check specific indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'order_payments_management_invoice';
```

## Troubleshooting

If you get errors about duplicate indexes:
- The migration might conflict with existing indexes
- Check if any of the indexes in 0009 already exist from 0008
- You may need to modify the migration to skip existing indexes

If Django still detects changes after applying migrations:
- Run `python3 manage.py makemigrations` to see what it detects
- Compare model definitions with migration files
- Ensure all model changes have corresponding migrations

