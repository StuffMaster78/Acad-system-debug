# Scalable Fine System - Complete Guide

## Overview

A comprehensive, scalable fine system that allows admins to create and manage any fine type dynamically, with configurable calculation methods, amounts, and rules.

---

## Key Features

### 1. **Admin-Configurable Fine Types**
- Admins can create unlimited fine types
- Each fine type has its own calculation method
- Website-specific or global fine types
- Cannot delete system-defined types (e.g., late submission)

### 2. **Flexible Calculation Methods**
- **Fixed Amount**: Set a specific dollar amount
- **Percentage**: Percentage of writer compensation or order total
- **Progressive Hourly**: Only for late submission (uses LatenessFineRule)

### 3. **Fine Type Configuration**
Each fine type can specify:
- Code (unique identifier)
- Name (display name)
- Description
- Calculation type (fixed/percentage/progressive_hourly)
- Amount or percentage
- Base amount (writer compensation or order total)
- Min/Max limits
- Website scope (specific website or global)

### 4. **Automatic & Manual Fine Issuance**
- Automatic: Late submission fines (progressive hourly)
- Manual: Admin can issue any fine type via API or Django Admin

### 5. **Backward Compatibility**
- Legacy `FineType` enum still supported
- Existing fines continue to work
- Gradual migration path

---

## Models

### FineTypeConfig

Admin-configurable fine type definition.

**Key Fields:**
- `code`: Unique identifier (e.g., 'quality_issue', 'privacy_violation')
- `name`: Display name
- `calculation_type`: 'fixed', 'percentage', or 'progressive_hourly'
- `fixed_amount`: Fixed amount (for 'fixed' type)
- `percentage`: Percentage (for 'percentage' type)
- `base_amount`: 'writer_compensation' or 'total_price'
- `min_amount`, `max_amount`: Limits
- `website`: Website-specific or None (global)
- `active`: Enable/disable fine type
- `is_system_defined`: 'system' or 'admin' (system types cannot be deleted)

### Fine (Enhanced)

- `fine_type`: Legacy enum field (backward compatibility)
- `fine_type_config`: ForeignKey to FineTypeConfig (new, preferred)

---

## API Endpoints

### Fine Type Management (Admin)

#### List Fine Types
**GET** `/api/v1/fines/api/fine-types/`

**Query Params:**
- `website_id`: Filter by website
- `code`: Filter by code

**Response:**
```json
[
  {
    "id": 1,
    "code": "quality_issue",
    "name": "Quality Issue",
    "description": "Fine for poor quality work",
    "calculation_type": "percentage",
    "percentage": "10.00",
    "base_amount": "writer_compensation",
    "min_amount": "5.00",
    "max_amount": "50.00",
    "active": true,
    ...
  }
]
```

#### Create Fine Type
**POST** `/api/v1/fines/api/fine-types/`

**Request Body:**
```json
{
  "code": "custom_violation",
  "name": "Custom Violation",
  "description": "Description of when this fine applies",
  "calculation_type": "fixed",
  "fixed_amount": "25.00",
  "website_id": 1,
  "active": true
}
```

#### Get Available Fine Types
**GET** `/api/v1/fines/api/fine-types/available_types/`

Returns fine types available for current website (website-specific + global).

#### Update Fine Type
**PUT/PATCH** `/api/v1/fines/api/fine-types/{id}/`

**Note:** System-defined fine types cannot have their `code` or `calculation_type` changed.

#### Delete Fine Type
**DELETE** `/api/v1/fines/api/fine-types/{id}/`

**Note:** System-defined fine types cannot be deleted.

### Fine Issuance (Admin)

#### Issue Fine
**POST** `/api/v1/fines/api/fines/issue/`

**Request Body:**
```json
{
  "order_id": 123,
  "fine_type_code": "quality_issue",
  "reason": "Poor grammar, multiple spelling errors, didn't follow instructions",
  "custom_amount": 30.00  // Optional: override configured amount
}
```

**Response:**
```json
{
  "id": 45,
  "order": 123,
  "fine_type": "quality_issue",
  "fine_type_config": 2,
  "fine_type_name": "Quality Issue",
  "amount": "30.00",
  "reason": "...",
  "status": "issued",
  ...
}
```

#### Get Available Fine Types for Issuance
**GET** `/api/v1/fines/api/fines/available-types/`

Returns list of fine types that can be issued for current website.

---

## Common Fine Types

### Predefined Fine Types

The system includes these default fine types:

1. **late_submission** (System-Defined)
   - Progressive hourly calculation
   - 5% first hour, 10% second hour, etc.

2. **quality_issue**
   - Percentage: 10% of writer compensation
   - Min: $5, Max: $50

3. **privacy_violation**
   - Fixed: $50

4. **excessive_revisions**
   - Percentage: 5% of writer compensation

5. **late_reassignment**
   - Percentage: 15% of writer compensation

6. **dropping_order_late**
   - Percentage: 20% of writer compensation
   - Min: $10

7. **wrong_files**
   - Fixed: $10

8. **plagiarism**
   - Fixed: $100

9. **inactivity**
   - Percentage: 25% of writer compensation

10. **comm_breach**
    - Fixed: $15

---

## Usage Examples

### Example 1: Admin Creates New Fine Type

```python
from fines.services.fine_type_service import FineTypeService

config = FineTypeService.create_fine_type(
    code='data_breach',
    name='Data Breach',
    created_by=admin_user,
    calculation_type='fixed',
    fixed_amount=200.00,
    description='Fine for data breach or security violation',
    website=None  # Global fine type
)
```

### Example 2: Admin Issues Quality Fine

```python
from fines.services.fine_issue_helpers import FineIssueHelpers

fine = FineIssueHelpers.issue_quality_fine(
    order=order,
    reason='Multiple grammatical errors, poor structure, didn\'t follow client instructions',
    issued_by=admin_user,
    custom_amount=35.00  # Override default 10% with fixed $35
)
```

### Example 3: Admin Issues Custom Fine via API

**POST** `/api/v1/fines/api/fines/issue/`
```json
{
  "order_id": 123,
  "fine_type_code": "privacy_violation",
  "reason": "Writer shared client information on social media",
  "custom_amount": 75.00
}
```

### Example 4: Admin Issues Fine with Percentage

```python
from fines.services.fine_type_service import FineTypeService

# Fine type config: 15% of writer compensation, min $10, max $100
fine = FineTypeService.issue_fine(
    order=order,
    fine_type_code='excessive_revisions',
    reason='Required 5 revisions due to writer errors',
    issued_by=admin_user
)
# Fine amount calculated: 15% of writer_compensation (within min/max limits)
```

### Example 5: Admin Creates Website-Specific Fine Type

```python
config = FineTypeService.create_fine_type(
    code='special_quality',
    name='Special Quality Standard',
    created_by=admin_user,
    website=specific_website,
    calculation_type='percentage',
    percentage=20.00,
    base_amount='writer_compensation',
    description='Higher quality standard for premium clients'
)
```

---

## Helper Functions

### FineIssueHelpers

Convenience methods for common fine types:

```python
from fines.services.fine_issue_helpers import FineIssueHelpers

# Quality fine
FineIssueHelpers.issue_quality_fine(order, reason, admin)

# Privacy violation
FineIssueHelpers.issue_privacy_violation_fine(order, reason, admin)

# Excessive revisions
FineIssueHelpers.issue_excessive_revisions_fine(order, reason, admin, revision_count=5)

# Late reassignment
FineIssueHelpers.issue_late_reassignment_fine(order, reason, admin)

# Dropping order late
FineIssueHelpers.issue_dropping_order_late_fine(order, reason, admin, hours_into_order=24)

# Wrong files
FineIssueHelpers.issue_wrong_files_fine(order, reason, admin)

# Plagiarism
FineIssueHelpers.issue_plagiarism_fine(order, reason, admin)

# Inactivity
FineIssueHelpers.issue_inactivity_fine(order, reason, admin, days_inactive=3)

# Communication breach
FineIssueHelpers.issue_communication_breach_fine(order, reason, admin)
```

---

## Workflow

### 1. Admin Creates Fine Type

```
Admin → Django Admin or API
  ↓
Create FineTypeConfig
  ↓
Set code, name, calculation_type, amounts
  ↓
Fine type now available for issuance
```

### 2. Admin Issues Fine

```
Admin → API: POST /fines/issue/
  {
    "order_id": 123,
    "fine_type_code": "quality_issue",
    "reason": "...",
    "custom_amount": 30.00  // Optional
  }
  ↓
FineTypeService.issue_fine()
  ↓
Get FineTypeConfig by code
  ↓
Calculate amount (or use custom_amount)
  ↓
Create Fine record
  ↓
Adjust writer compensation
  ↓
Return Fine
```

### 3. Writer Disputes Fine

Same as before - uses existing dispute workflow.

---

## Django Admin

### FineTypeConfig Admin
- Full CRUD interface
- Fieldsets organized by category
- System-defined types have protected fields
- Cannot delete system-defined types

### Fine Admin
- Enhanced with `fine_type_config` field
- Shows both legacy `fine_type` and new `fine_type_config`
- Search by fine type code or name

---

## Migration Path

### Step 1: Run Migrations
```bash
python manage.py makemigrations fines
python manage.py migrate
```

### Step 2: Initialize Default Fine Types
```python
from fines.services.initialize_default_fine_types import initialize_default_fine_types

# Create global default fine types
initialize_default_fine_types()

# Or create for specific website
initialize_default_fine_types(website=specific_website)
```

### Step 3: Existing Fines
- Existing fines continue to work (using legacy `fine_type` field)
- New fines use `fine_type_config`
- Both fields can coexist

---

## Best Practices

1. **Use Fine Type Codes Consistently**
   - Use snake_case (e.g., 'quality_issue', not 'Quality Issue')
   - Keep codes descriptive and unique

2. **Set Reasonable Limits**
   - Always set `min_amount` and `max_amount` for percentage fines
   - Prevents accidental excessive fines

3. **Website-Specific Types**
   - Use website-specific fine types for custom client requirements
   - Global types apply to all websites

4. **Document Fine Types**
   - Always provide clear `description`
   - Helps admins understand when to use each type

5. **Test Calculations**
   - Test fine calculations with sample orders
   - Verify min/max limits work correctly

---

## Error Handling

### Common Errors

1. **Fine Type Not Found**
   - Error: "No active fine type config found for code 'xyz'"
   - Solution: Create FineTypeConfig first

2. **Invalid Calculation Type**
   - Error: "Progressive hourly only available for late_submission"
   - Solution: Use 'fixed' or 'percentage' for other types

3. **Missing Required Fields**
   - Error: "Fixed amount required for 'fixed' calculation type"
   - Solution: Provide `fixed_amount` when `calculation_type='fixed'`

4. **Min > Max**
   - Error: "Min amount cannot be greater than max amount"
   - Solution: Adjust min/max values

---

## Scalability Features

1. **Unlimited Fine Types**: Admins can create any number of fine types
2. **Flexible Calculation**: Three calculation methods support most use cases
3. **Website-Specific**: Fine types can be scoped to specific websites
4. **Extensible**: Easy to add new calculation types in the future
5. **Backward Compatible**: Existing code continues to work

---

## Future Enhancements

1. **Fine Templates**: Pre-defined fine templates for common scenarios
2. **Fine Rules Engine**: Conditional fine application based on order attributes
3. **Fine Schedules**: Automatic fine escalation over time
4. **Fine Analytics**: Dashboard showing fine trends by type
5. **Fine Exemptions**: Exempt certain writers or order types from specific fines

