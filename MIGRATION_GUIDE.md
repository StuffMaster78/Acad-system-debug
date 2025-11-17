# Migration Guide - Manual Creation

## Current Status

Django detected several missing migrations. Some have been created manually, others need to be created.

## ✅ Already Created

1. `discounts/0003_seasonalevent.py` - Proxy model
2. `order_configs/0004_alter_englishtype_code_alter_englishtype_name_and_more.py` - Field alterations
3. `order_payments_management/0009_add_invoice_indexes.py` - Invoice indexes (created earlier)

## ⚠️ Recommended Approach

Given the complexity of the remaining migrations (especially index renames), you have two options:

### Option 1: Let Django Auto-Generate (Recommended)

Since Django has already detected all the changes, the easiest approach is to let Django create the migrations:

```bash
docker-compose exec -T web python3 manage.py makemigrations
```

Then review the generated files before applying:

```bash
docker-compose exec -T web python3 manage.py migrate
```

### Option 2: Apply Existing Migrations First

Apply the migrations we've already created:

```bash
# Apply invoice indexes migration
docker-compose exec -T web python3 manage.py migrate order_payments_management 0009_add_invoice_indexes

# Apply other completed migrations
docker-compose exec -T web python3 manage.py migrate discounts 0003_seasonalevent
docker-compose exec -T web python3 manage.py migrate order_configs 0004_alter_englishtype_code_alter_englishtype_name_and_more
```

Then run `makemigrations` again to see what's left.

## Remaining Migrations to Create

The following migrations still need to be created (or auto-generated):

1. **order_payments_management/0010** - Complex: DiscountUsage proxy, Invoice Meta changes, index renames, field alterations
2. **orders/0007** - Index renames, writerprogress changes
3. **refunds/0002** - Field alterations
4. **reviews_system/0002** - Field alterations
5. **service_pages_management/0004** - New models and fields
6. **special_orders/0003** - Field additions
7. **communications** - (details unknown)

## Note on Index Renames

Django wants to rename indexes because manually created indexes have different names than Django's auto-generated convention. This is safe - it's just updating names. The indexes themselves are correct.

## Quick Fix: Apply Invoice Indexes Now

If you just want to apply the invoice indexes optimization we created:

```bash
docker-compose exec -T web python3 manage.py migrate order_payments_management 0009_add_invoice_indexes
```

This will apply the performance optimizations without waiting for other migrations.
