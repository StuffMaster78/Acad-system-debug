# Dropdown Options API Documentation

## Overview

All dropdown lists in the system now draw from the database or exposed enums. This ensures consistency, allows admin customization, and provides a single source of truth.

## Unified Dropdown Endpoint

### Get All Dropdown Options

**GET** `/api/v1/dropdown-options/`

Returns all dropdown options in a single response.

**Query Parameters:**
- `website_id` (optional): Filter order configs by specific website
- `include_enums` (default: `true`): Include enum choices (status, payment types, etc.)
- `include_configs` (default: `true`): Include order configuration options
- `include_websites` (default: `true`): Include websites list
- `include_users` (default: `false`): Include users list (admin only)

**Response:**
```json
{
  "order_configs": {
    "paper_types": [
      {"id": 1, "name": "Essay", "website_id": 1},
      {"id": 2, "name": "Research Paper", "website_id": 1}
    ],
    "formatting_styles": [
      {"id": 1, "name": "APA", "website_id": 1},
      {"id": 2, "name": "MLA", "website_id": 1}
    ],
    "subjects": [
      {"id": 1, "name": "English", "is_technical": false, "website_id": 1},
      {"id": 2, "name": "Mathematics", "is_technical": true, "website_id": 1}
    ],
    "academic_levels": [
      {"id": 1, "name": "High School", "website_id": 1},
      {"id": 2, "name": "College", "website_id": 1}
    ],
    "types_of_work": [
      {"id": 1, "name": "Writing", "website_id": 1},
      {"id": 2, "name": "Editing", "website_id": 1}
    ],
    "english_types": [
      {"id": 1, "name": "US English", "code": "US", "website_id": 1},
      {"id": 2, "name": "UK English", "code": "UK", "website_id": 1}
    ]
  },
  "enums": {
    "order_status": [
      {"value": "pending", "label": "Pending"},
      {"value": "in_progress", "label": "In Progress"}
    ],
    "payment_status": [
      {"value": "pending", "label": "Pending"},
      {"value": "completed", "label": "Completed"}
    ],
    "payment_types": [
      {"value": "standard", "label": "Standard Order"},
      {"value": "invoice", "label": "Standalone Invoice"}
    ],
    "spacing_options": [
      {"value": "single", "label": "Single"},
      {"value": "double", "label": "Double"}
    ],
    "fine_types": [
      {"value": "late_submission", "label": "Late Submission"},
      {"value": "quality", "label": "Quality Penalty"}
    ]
  },
  "websites": [
    {"id": 1, "name": "Website 1", "domain": "example.com"}
  ],
  "class_duration_options": [
    {"id": 1, "class_code": "15-16", "label": "15–16 weeks", "website_id": 1}
  ]
}
```

### Get Dropdown Options by Category

**GET** `/api/v1/dropdown-options/{category}/`

Get dropdown options for a specific category.

**Categories:**
- `order_configs` - All order configuration options
- `enums` - All enum choices
- `websites` - Website list
- `users` - User list (admin only)
- `paper_types` - Paper types only
- `subjects` - Subjects only
- `academic_levels` - Academic levels only
- `formatting_styles` - Formatting styles only
- `types_of_work` - Types of work only
- `english_types` - English types only
- `class_duration_options` - Class duration options

**Example:**
```bash
GET /api/v1/dropdown-options/paper_types/?website_id=1
```

**Response:**
```json
[
  {"id": 1, "name": "Essay", "website_id": 1},
  {"id": 2, "name": "Research Paper", "website_id": 1}
]
```

## Order Configs Endpoint (Alternative)

You can also use the existing order configs endpoints:

**GET** `/api/v1/order-configs/api/paper-types/?website_id=1`
**GET** `/api/v1/order-configs/api/subjects/?website_id=1`
**GET** `/api/v1/order-configs/api/academic-levels/?website_id=1`
**GET** `/api/v1/order-configs/api/formatting-styles/?website_id=1`
**GET** `/api/v1/order-configs/api/types-of-work/?website_id=1`
**GET** `/api/v1/order-configs/api/english-types/?website_id=1`

**Or get all at once:**
**GET** `/api/v1/order-configs/api/management/dropdown-options/?website_id=1`

## Database-Driven Options

All these options are stored in the database and can be managed by admins:

1. **Paper Types** - `order_configs.PaperType`
2. **Formatting Styles** - `order_configs.FormattingandCitationStyle`
3. **Subjects** - `order_configs.Subject`
4. **Academic Levels** - `order_configs.AcademicLevel`
5. **Types of Work** - `order_configs.TypeOfWork`
6. **English Types** - `order_configs.EnglishType`
7. **Class Duration Options** - `class_management.ClassDurationOption`
8. **Websites** - `websites.Website`
9. **Users** - `users.User`

## Enum-Based Options

These are defined as enums but exposed via API:

1. **Order Status** - `OrderStatus` enum
2. **Payment Status** - `OrderPaymentStatus` enum
3. **Payment Types** - `PAYMENT_TYPE_CHOICES`
4. **Spacing Options** - `SpacingOptions` enum
5. **Dispute Status** - `DisputeStatusEnum`
6. **Fine Types** - `FineType` TextChoices
7. **Fine Status** - `FineStatus` TextChoices

## Multi-Tenant Support

All order configuration options are filtered by website:
- Superadmins see all websites' options
- Admins see only their website's options
- Clients see only their website's options

## Performance

- All queries use `select_related()` for optimization
- Results are ordered for consistent display
- Category-specific endpoints allow loading only needed data

## Usage Examples

### Frontend: Load All Dropdowns
```javascript
// Load all dropdown options
const response = await fetch('/api/v1/dropdown-options/?website_id=1', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Use in dropdowns
const paperTypes = data.order_configs.paper_types;
const orderStatuses = data.enums.order_status;
```

### Frontend: Load Specific Category
```javascript
// Load only paper types
const response = await fetch('/api/v1/dropdown-options/paper_types/?website_id=1', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const paperTypes = await response.json();
```

### Frontend: Load Enums Only
```javascript
// Load only enum choices (no database queries)
const response = await fetch('/api/v1/dropdown-options/enums/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const enums = await response.json();
```

## Benefits

1. ✅ **Single Source of Truth** - All dropdowns use database or enums
2. ✅ **Admin Customizable** - Admins can add/edit options via admin panel
3. ✅ **Multi-Tenant** - Automatically filtered by website
4. ✅ **Performance Optimized** - Uses select_related and efficient queries
5. ✅ **Consistent API** - Unified endpoint for all dropdown needs
6. ✅ **Flexible** - Can load all or specific categories

