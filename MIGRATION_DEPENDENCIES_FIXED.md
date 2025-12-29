# Migration Dependencies Fixed

## Summary

All migration dependency issues have been resolved. The test database can now be created and migrations run successfully.

## Issues Fixed

### 1. **Users → Notifications System Dependency**
- **Problem**: `users.0001_initial` and `users.0005_*` migrations depended on `notifications_system` migrations that weren't being discovered properly during test database creation.
- **Solution**: 
  - Ensured `notifications_system` is in `INSTALLED_APPS` for test settings
  - Removed `MIGRATION_MODULES` exclusion for PostgreSQL tests
  - Verified migration order is correct

### 2. **Pricing App Missing Migrations**
- **Problem**: The `pricing` app had no migrations but contains models with ForeignKeys to `User`, causing issues when Django tried to sync unmigrated apps before running migrations.
- **Solution**: Created `pricing/migrations/0001_initial.py` migration for `PricingCalculatorSession` model.

### 3. **Blog Pages Management Migration 0013**
- **Problem**: Migration tried to rename an index that was already renamed in migration 0011 or 0012.
- **Solution**: Updated migration to use conditional SQL with `IF EXISTS` checks.

### 4. **Editor Management Migration 0010**
- **Problem**: Migration tried to rename indexes that were already renamed in migration 0009.
- **Solution**: Replaced `RenameIndex` operations with `RunPython` that conditionally renames indexes only if old names exist.

### 5. **Website Fixture Duplicate Key**
- **Problem**: Test fixture tried to create a website with a name that already existed.
- **Solution**: Changed `Website.objects.create()` to `Website.objects.get_or_create()` in `conftest.py`.

## Files Modified

1. `backend/writing_system/settings_test.py` - Fixed PostgreSQL test database configuration
2. `backend/pricing/migrations/0001_initial.py` - Created (new migration file)
3. `backend/blog_pages_management/migrations/0013_*.py` - Fixed conditional index rename
4. `backend/editor_management/migrations/0010_*.py` - Fixed conditional index rename
5. `backend/conftest.py` - Fixed website fixture to use `get_or_create`

## Test Status

✅ **Migrations now run successfully**
- All migrations apply without errors
- Test database is created correctly
- Migration dependency graph is valid

⚠️ **Remaining Issue**
- Some tests may have transaction management issues (separate from migration dependencies)
- This is a test implementation issue, not a migration problem

## Next Steps

1. Run full test suite to identify any remaining test issues
2. Fix any transaction management errors in individual tests
3. Verify test coverage after all tests pass

