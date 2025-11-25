# Class Simulation and Configuration Guide

This guide explains how to simulate classes and configure class bundle settings in the system.

## Overview

The class management system supports:
- **Class Duration Options**: Configurable duration periods (e.g., 8-10 weeks, 15-16 weeks)
- **Class Bundle Configs**: Pricing configurations for different academic levels and bundle sizes
- **Class Bundles**: Actual class bundles purchased by clients

## Seeding Class Configurations

### Basic Usage

Seed class configurations for all active websites:

```bash
docker-compose exec web python manage.py seed_class_configs
```

### Options

#### Seed for Specific Website
```bash
docker-compose exec web python manage.py seed_class_configs --website-id 1
```

#### Clear Existing Data First
```bash
docker-compose exec web python manage.py seed_class_configs --clear
```

#### Create Sample Class Bundles
```bash
docker-compose exec web python manage.py seed_class_configs --create-bundles
```

#### Combined Options
```bash
docker-compose exec web python manage.py seed_class_configs --clear --create-bundles
```

## What Gets Created

### Duration Options
The command creates the following duration options for each website:
- **8-10 weeks** (class_code: `8-10`)
- **12-14 weeks** (class_code: `12-14`)
- **15-16 weeks** (class_code: `15-16`)
- **16-18 weeks** (class_code: `16-18`)

### Bundle Configurations

For each duration option, the command creates configurations for:

#### Undergraduate Level (`undergrad`)
- 1 class: $150.00/class
- 2 classes: $145.00/class
- 3 classes: $140.00/class
- 4 classes: $135.00/class
- 5 classes: $130.00/class
- 6 classes: $125.00/class
- 8 classes: $120.00/class
- 10 classes: $115.00/class

#### Graduate Level (`grad`)
- 1 class: $200.00/class
- 2 classes: $195.00/class
- 3 classes: $190.00/class
- 4 classes: $185.00/class
- 5 classes: $180.00/class
- 6 classes: $175.00/class
- 8 classes: $170.00/class
- 10 classes: $165.00/class

**Total Configurations**: 4 durations × 2 levels × 8 bundle sizes = **64 configurations per website**

## Sample Class Bundles

When using `--create-bundles`, the command will:
1. Find active clients (up to 5)
2. Find active writers (up to 3)
3. Create 2-3 sample bundles per website
4. Assign bundles to clients and writers
5. Set appropriate dates and pricing

## Managing Configurations

### Via Django Admin

1. Navigate to Django Admin
2. Go to **Class Management** section
3. Access:
   - **Class Duration Options**: Manage duration periods
   - **Class Bundle Configs**: Manage pricing configurations

### Via API

Use the `ClassBundleConfigViewSet` API endpoints:

- **List configs**: `GET /api/v1/class-management/configs/`
- **Get specific config**: `GET /api/v1/class-management/configs/{id}/`
- **Create config**: `POST /api/v1/class-management/configs/`
- **Update config**: `PUT /api/v1/class-management/configs/{id}/`
- **Delete config**: `DELETE /api/v1/class-management/configs/{id}/`

### Via Admin Dashboard

Access class bundle management through:
- **Admin Dashboard** → **Class Bundles** section
- View, create, and manage class bundles
- Configure installments and deposits

## Configuration Structure

### ClassDurationOption
```python
{
    "website": Website,
    "class_code": "15-16",  # Short identifier
    "label": "15–16 weeks",  # Human-readable
    "is_active": True
}
```

### ClassBundleConfig
```python
{
    "website": Website,
    "duration": ClassDurationOption,
    "level": "undergrad" | "grad",
    "bundle_size": 1-10,  # Number of classes
    "price_per_class": Decimal,
    "is_active": True
}
```

### ClassBundle
```python
{
    "client": User,
    "website": Website,
    "assigned_writer": User,
    "config": ClassBundleConfig,  # Optional if manual
    "pricing_source": "config" | "manual",
    "duration": "15-16",
    "level": "undergrad" | "grad",
    "bundle_size": 5,
    "price_per_class": Decimal,
    "number_of_classes": 5,
    "start_date": Date,
    "end_date": Date,
    "total_price": Decimal,
    "status": "not_started" | "in_progress" | "exhausted" | "completed"
}
```

## Customizing Configurations

### Modify Pricing

Edit the `bundle_configs` list in `seed_class_configs.py`:

```python
bundle_configs = [
    ('undergrad', 1, Decimal('150.00')),
    ('undergrad', 2, Decimal('145.00')),
    # Add more configurations...
]
```

### Add Duration Options

Edit the `duration_configs` list:

```python
duration_configs = [
    {'class_code': '8-10', 'label': '8–10 weeks'},
    {'class_code': '12-14', 'label': '12–14 weeks'},
    # Add more durations...
]
```

## Best Practices

1. **Test First**: Run without `--create-bundles` first to verify configurations
2. **Clear When Needed**: Use `--clear` when you want to reset all configurations
3. **Website-Specific**: Use `--website-id` for multi-tenant setups
4. **Backup**: Always backup database before clearing configurations
5. **Review Pricing**: Verify pricing makes sense for your business model

## Troubleshooting

### No Websites Found
- Ensure at least one website exists with `is_active=True`
- Check website creation in Django admin

### No Clients/Writers for Bundles
- Create test users with roles `client` and `writer`
- Ensure users have `is_active=True`

### Duplicate Configurations
- Configs are unique by `(duration, level, bundle_size)`
- Existing configs will be updated, not duplicated
- Use `--clear` to start fresh

## Related Documentation

- [Class Management Workflow](../CLASS_MANAGEMENT_WORKFLOW.md)
- [Class Bundle Admin Service](../services/class_bundle_admin.py)
- [Class Pricing Service](../services/pricing.py)

