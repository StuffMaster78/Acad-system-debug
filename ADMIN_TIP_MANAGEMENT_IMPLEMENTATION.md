# Admin Tip Management & Earnings Tracking Implementation

## Overview

Complete admin/superadmin dashboard for tracking tip earnings, showing:
- **Total tips** and amounts
- **Writer earnings** (what writers received)
- **Platform profit** (what the company retained)
- **Breakdowns** by tip type, writer level, payment status
- **Analytics** with trends and top performers
- **Detailed earnings** reports

## Implementation Status

### ✅ Completed

1. **AdminTipManagementViewSet** (`admin_management/views.py`)
   - `dashboard()`: Tip statistics with earnings breakdown
   - `list_tips()`: List all tips with filtering and pagination
   - `analytics()`: Trends, breakdowns, and top performers
   - `earnings()`: Detailed earnings breakdown by level, type, and time period

2. **URL Registration** (`admin_management/urls.py`)
   - Registered at `/admin-management/tips/`
   - All endpoints accessible via ViewSet actions

3. **Frontend Integration**
   - `admin-tips-api.js`: API service file
   - Added to `src/api/index.js` exports
   - Vue component template in integration guide

## API Endpoints

### Dashboard
```http
GET /api/v1/admin-management/tips/dashboard/?days=30
```
Returns:
- Summary: total tips, amounts, writer earnings, platform profit
- Recent summary (last N days)
- Payment status breakdown
- Type breakdown (direct, order, class)
- Level breakdown (by writer level)

### List Tips
```http
GET /api/v1/admin-management/tips/list_tips/
GET /api/v1/admin-management/tips/list_tips/?tip_type=order
GET /api/v1/admin-management/tips/list_tips/?payment_status=completed
GET /api/v1/admin-management/tips/list_tips/?writer_id=123
GET /api/v1/admin-management/tips/list_tips/?client_id=456
GET /api/v1/admin-management/tips/list_tips/?date_from=2024-01-01&date_to=2024-12-31
GET /api/v1/admin-management/tips/list_tips/?limit=50&offset=0
```
Returns:
- Paginated list of tips with full details
- Summary statistics for filtered results

### Analytics
```http
GET /api/v1/admin-management/tips/analytics/?days=90
```
Returns:
- Monthly/weekly/daily trends
- Breakdowns by type and level
- Top 10 writers by earnings
- Top 10 clients by tips sent

### Earnings
```http
GET /api/v1/admin-management/tips/earnings/
GET /api/v1/admin-management/tips/earnings/?date_from=2024-01-01&date_to=2024-12-31
```
Returns:
- Overall earnings statistics
- Earnings by writer level
- Earnings by tip type
- Monthly earnings (last 12 months)

## Data Visibility

### Admins/Superadmins See:
- ✅ Full tip amount (`tip_amount`)
- ✅ Writer earnings (`writer_earning`)
- ✅ Platform profit (`platform_profit`)
- ✅ Writer percentage (`writer_percentage`)
- ✅ All tip details
- ✅ Payment information

### Writers See (via TipListSerializer):
- ❌ Full tip amount (hidden)
- ✅ Only their share (`amount_received` = `writer_earning`)
- ❌ Platform profit (hidden)
- ❌ Writer percentage (hidden)

## Example Response

### Dashboard Response
```json
{
  "summary": {
    "total_tips": 150,
    "total_tip_amount": 7500.00,
    "total_writer_earnings": 4500.00,
    "total_platform_profit": 3000.00,
    "avg_tip_amount": 50.00,
    "avg_writer_percentage": 60.00
  },
  "recent_summary": {
    "days": 30,
    "total_tips": 45,
    "total_tip_amount": 2250.00,
    "total_writer_earnings": 1350.00,
    "total_platform_profit": 900.00
  },
  "payment_status": {
    "completed": 140,
    "pending": 5,
    "processing": 3,
    "failed": 2
  },
  "type_breakdown": [
    {
      "tip_type": "direct",
      "count": 50,
      "total_amount": 2500.00,
      "writer_earnings": 1500.00,
      "platform_profit": 1000.00
    },
    {
      "tip_type": "order",
      "count": 80,
      "total_amount": 4000.00,
      "writer_earnings": 2400.00,
      "platform_profit": 1600.00
    },
    {
      "tip_type": "class",
      "count": 20,
      "total_amount": 1000.00,
      "writer_earnings": 600.00,
      "platform_profit": 400.00
    }
  ],
  "level_breakdown": [
    {
      "writer_level__name": "Senior Writer",
      "count": 60,
      "total_amount": 3600.00,
      "writer_earnings": 2520.00,
      "platform_profit": 1080.00,
      "avg_percentage": 70.00
    },
    {
      "writer_level__name": "Junior Writer",
      "count": 90,
      "total_amount": 3900.00,
      "writer_earnings": 1980.00,
      "platform_profit": 1920.00,
      "avg_percentage": 50.00
    }
  ]
}
```

### List Tips Response
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "tip_type": "order",
      "tip_type_display": "Order-Based Tip",
      "tip_reason": "Great work!",
      "sent_at": "2024-01-15T10:30:00Z",
      "writer_name": "John Doe",
      "writer_username": "johndoe",
      "client_name": "Jane Smith",
      "client_username": "janesmith",
      "order_title": "Research Paper on AI",
      "amount_received": "30.00",
      "full_tip_amount": "50.00",
      "writer_percentage_display": "60%",
      "payment_status": "completed"
    }
  ],
  "summary": {
    "total_tip_amount": 7500.00,
    "total_writer_earnings": 4500.00,
    "total_platform_profit": 3000.00
  }
}
```

## Frontend Integration

### Copy API File
```bash
cp frontend_integration/admin-tips-api.js /path/to/frontend/src/api/admin/tips.js
```

### Usage Example
```javascript
import { adminTipsApi } from '@/api/admin/tips'

// Get dashboard
const dashboard = await adminTipsApi.getDashboard({ days: 30 })
console.log('Total Platform Profit:', dashboard.data.summary.total_platform_profit)
console.log('Total Writer Earnings:', dashboard.data.summary.total_writer_earnings)

// List tips
const tips = await adminTipsApi.listTips({
  payment_status: 'completed',
  tip_type: 'order',
  limit: 50
})

// Get analytics
const analytics = await adminTipsApi.getAnalytics({ days: 90 })

// Get earnings
const earnings = await adminTipsApi.getEarnings({
  date_from: '2024-01-01',
  date_to: '2024-12-31'
})
```

## Key Features

1. **Complete Earnings Visibility**
   - See exactly what writers earned
   - See exactly what platform retained
   - Breakdown by writer level (percentage-based)

2. **Comprehensive Filtering**
   - Filter by tip type (direct, order, class)
   - Filter by payment status
   - Filter by writer or client
   - Filter by date range

3. **Analytics & Trends**
   - Monthly/weekly/daily trends
   - Top performers (writers and clients)
   - Performance by writer level

4. **Earnings Reports**
   - Overall earnings statistics
   - Breakdown by writer level
   - Breakdown by tip type
   - Monthly earnings history

## Notes

- All endpoints require admin or superadmin permissions
- Website filtering is applied automatically if user has website context
- Only completed tips are included in earnings calculations
- All monetary values are returned as floats for JSON compatibility
- Pagination is supported for list endpoints

