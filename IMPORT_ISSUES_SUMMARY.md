# Import Issues Summary & Resolution Plan

## Current Issue

When creating `models/` subdirectories alongside existing `models.py` files, Python treats `app.models` as the package (the `__init__.py`), not the file. This causes circular import issues.

## Files Affected

1. **tickets/models/** - Removed (moved `sla_timers.py` to root)
2. **websites/models/** - Needs proper exports of all models
3. **support_management/models/** - Needs proper exports of all models
4. **analytics/models/** - Should be fine (new app, no existing models.py)

## Solutions Applied

### ✅ Tickets App
- Moved `sla_timers.py` to `tickets/` root
- Removed `tickets/models/` directory
- Updated imports to use string references

### ⚠️ Websites App
- Created `websites/models/__init__.py` to export models
- Still needs to export ALL models from parent `models.py`
- Current exports: Website, WebsiteActionLog, WebsiteStaticPage, WebsiteSettings, WebsiteTermsAcceptance, User

### ⚠️ Support Management App
- Created `support_management/models/__init__.py` with dynamic import
- Using `globals().update()` to export all parent models
- May need refinement

## Recommended Approach

For apps with existing `models.py` files, consider:

1. **Option A**: Don't create `models/` subdirectory - put new models in separate files and import them in `models.py`
2. **Option B**: Move all models to `models/` subdirectory and remove `models.py`
3. **Option C**: Use proper `__init__.py` that exports everything (current approach)

## Next Steps

1. Fix remaining import issues in `websites/models/__init__.py` and `support_management/models/__init__.py`
2. Test Django startup: `python manage.py check`
3. Apply migrations once imports are fixed
4. Continue with serializers and ViewSets

