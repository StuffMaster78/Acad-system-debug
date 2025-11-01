# Loyalty Points Redemption System

## Overview

Complete loyalty points redemption system allowing clients to redeem accumulated loyalty points for various rewards including discounts, cash/wallet credit, products, services, and vouchers.

## Features

### 1. Redemption Categories
- Organize redemption items into categories (Discounts, Products, Services, Cash, etc.)
- Admin-configurable categories with sort ordering
- Active/inactive status per category

### 2. Redemption Items
- **Types**: Discount Code, Cash/Wallet Credit, Physical Product, Service Credit, Voucher/Code
- **Configuration**:
  - Points required
  - Stock quantity (optional, for limited items)
  - Maximum redemptions per client
  - Minimum loyalty tier required
  - Discount amounts/percentages (for discount types)
  
### 3. Redemption Workflow

#### Client Flow:
1. **Browse Items**: View available redemption items filtered by category
2. **Check Eligibility**: System validates:
   - Sufficient points
   - Item availability (stock)
   - Tier requirements
   - Per-client redemption limits
3. **Request Redemption**: Submit redemption request
4. **Auto-approval**: Discounts and cash credits auto-approve
5. **Receive Fulfillment**: Get discount code, wallet credit, or voucher

#### Admin Flow:
1. **Manage Items**: Create/edit redemption items
2. **Review Requests**: View pending redemption requests
3. **Approve/Reject**: Process manual redemptions (products, services)
4. **Fulfill**: Mark as fulfilled and provide fulfillment details
5. **Track**: Monitor redemption history and statistics

### 4. Fulfillment Types

#### Discount Code (`discount`)
- Automatically generates unique discount code
- Creates `Discount` record in system
- Configurable discount amount or percentage
- Valid for 90 days by default

#### Cash/Wallet Credit (`cash`)
- Automatically credits client's wallet
- Creates wallet transaction record
- Instant fulfillment

#### Voucher/Code (`voucher`)
- Generates unique voucher code
- Stored in `fulfillment_code` field
- Can be used for external systems

#### Physical Product (`product`)
- Requires manual admin approval
- Admin provides fulfillment details (tracking, delivery address)
- Stock decremented on approval

#### Service Credit (`service`)
- Requires manual admin approval
- Admin provides service details in fulfillment

## API Endpoints

### Redemption Categories
```
GET    /api/v1/loyalty-management/redemption-categories/     # List categories
POST   /api/v1/loyalty-management/redemption-categories/     # Create (admin)
GET    /api/v1/loyalty-management/redemption-categories/{id}/ # Retrieve
PUT    /api/v1/loyalty-management/redemption-categories/{id}/ # Update (admin)
DELETE /api/v1/loyalty-management/redemption-categories/{id}/ # Delete (admin)
```

### Redemption Items
```
GET    /api/v1/loyalty-management/redemption-items/          # List items (filtered by category, active)
POST   /api/v1/loyalty-management/redemption-items/          # Create (admin)
GET    /api/v1/loyalty-management/redemption-items/{id}/     # Retrieve (includes can_redeem check)
PUT    /api/v1/loyalty-management/redemption-items/{id}/     # Update (admin)
DELETE /api/v1/loyalty-management/redemption-items/{id}/     # Delete (admin)

Query Params:
  ?category={category_id}  # Filter by category
```

### Redemption Requests
```
GET    /api/v1/loyalty-management/redemption-requests/       # List (own for clients, all for admins)
POST   /api/v1/loyalty-management/redemption-requests/       # Create request
GET    /api/v1/loyalty-management/redemption-requests/{id}/  # Retrieve
POST   /api/v1/loyalty-management/redemption-requests/{id}/approve/  # Approve (admin)
POST   /api/v1/loyalty-management/redemption-requests/{id}/reject/   # Reject (admin)
POST   /api/v1/loyalty-management/redemption-requests/{id}/cancel/   # Cancel (client/admin)

Query Params:
  ?status={pending|approved|fulfilled|rejected|cancelled}  # Filter by status
```

## Request/Response Examples

### Create Redemption Request
```json
POST /api/v1/loyalty-management/redemption-requests/
{
  "item_id": 5,
  "fulfillment_details": {
    "delivery_address": "123 Main St"  // Optional, for products
  }
}

Response:
{
  "id": 123,
  "item_name": "$10 Discount",
  "points_used": 1000,
  "status": "fulfilled",  // Auto-approved for discounts/cash
  "fulfillment_code": "LOYALTY-A1B2C3D4",
  "requested_at": "2024-01-15T10:30:00Z"
}
```

### Approve Redemption (Admin)
```json
POST /api/v1/loyalty-management/redemption-requests/123/approve/

Response:
{
  "id": 123,
  "status": "fulfilled",
  "fulfillment_code": "PRODUCT-ABC123",
  "fulfilled_at": "2024-01-15T10:35:00Z"
}
```

### List Available Items
```json
GET /api/v1/loyalty-management/redemption-items/?category=1

Response:
[
  {
    "id": 1,
    "name": "$10 Discount Code",
    "category_name": "Discounts",
    "points_required": 1000,
    "redemption_type": "discount",
    "discount_amount": "10.00",
    "is_available": true,
    "can_redeem": {
      "can_redeem": true,
      "message": "Can redeem"
    }
  },
  {
    "id": 2,
    "name": "Free Writing Service",
    "category_name": "Services",
    "points_required": 2500,
    "redemption_type": "service",
    "is_available": true,
    "can_redeem": {
      "can_redeem": false,
      "message": "Insufficient points. Required: 2500, Available: 1200"
    }
  }
]
```

## Models

### RedemptionCategory
- `name`: Category name
- `description`: Category description
- `is_active`: Active status
- `sort_order`: Display order
- `website`: Multi-tenant support

### RedemptionItem
- `category`: Category FK
- `name`: Item name
- `description`: Item description
- `points_required`: Points needed
- `redemption_type`: Type of redemption
- `discount_amount`/`discount_percentage`: For discount types
- `stock_quantity`: Available stock (None = unlimited)
- `total_redemptions`: Redemption counter
- `max_per_client`: Max redemptions per client
- `min_tier_level`: Required loyalty tier
- `is_active`: Active status

### RedemptionRequest
- `client`: Client making request
- `item`: Item being redeemed
- `points_used`: Points deducted
- `status`: pending|approved|fulfilled|rejected|cancelled
- `fulfillment_code`: Generated code/voucher
- `fulfillment_details`: Additional fulfillment info (JSON)
- `approved_by`/`fulfilled_by`: Admin tracking
- `rejection_reason`: Reason if rejected

## Business Rules

1. **Points Deduction**: Points are deducted immediately when redemption is approved
2. **Stock Management**: Stock decremented on approval (if applicable)
3. **Auto-approval**: Discounts and cash credits auto-approve
4. **Manual Approval**: Products and services require admin approval
5. **Cancellation**: Clients can cancel pending requests; approved requests refund points if not fulfilled
6. **Tier Requirements**: Items can require minimum loyalty tier
7. **Per-Client Limits**: Enforced to prevent abuse

## Integration Points

- **Discount System**: Creates discount codes automatically
- **Wallet System**: Credits wallet for cash redemptions
- **Notifications**: Sends notifications on approval/rejection
- **Analytics**: Tracks redemption statistics

## Admin Interface

All models registered in Django Admin with:
- List displays with key fields
- Filtering by status, category, website
- Search functionality
- Bulk actions (approve/reject requests)
- Read-only fields for audit tracking

