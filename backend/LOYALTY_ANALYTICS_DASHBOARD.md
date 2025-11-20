# Loyalty Analytics Dashboard

## Overview

Comprehensive analytics dashboard for tracking loyalty program performance, client engagement, redemption patterns, and program effectiveness.

## Features

### 1. Overall Metrics
- **Total Active Clients**: Clients with loyalty points > 0
- **Total Points Issued**: Points awarded in period
- **Total Points Redeemed**: Points redeemed in period
- **Total Points Balance**: Outstanding points across all clients
- **Redemption Statistics**: Total redemptions and value

### 2. Trend Analysis
- **Points Trend**: Daily points issued/redeemed/balance over time
- **Redemption Trend**: Redemption frequency over time
- **Engagement Trend**: Client engagement patterns

### 3. Tier Distribution
- **Tier Breakdown**: Count of clients in each tier (Bronze, Silver, Gold, Platinum)
- **Tier Percentages**: Distribution percentages
- **Tier Thresholds**: Points required for each tier

### 4. Redemption Insights
- **Top Redemption Items**: Most popular redemption items
- **Redemption Categories**: Popularity by category
- **Redemption Patterns**: When clients redeem most
- **Average Redemption Value**: Average points per redemption

### 5. Engagement Metrics
- **Engagement Rate**: Percentage of clients actively using loyalty program
- **Redemption Rate**: Percentage of active clients who redeemed
- **Average Points per Client**: Mean points balance
- **Client Lifetime Value**: Based on loyalty points accumulated

### 6. Configurable Widgets
- Customizable dashboard widgets
- Multiple widget types (charts, metrics, tables)
- Position ordering
- Visibility toggles
- Widget-specific configurations

## API Endpoints

### Analytics Overview
```
GET    /api/v1/loyalty-management/analytics/              # List analytics records
GET    /api/v1/loyalty-management/analytics/{id}/         # Retrieve specific analytics
POST   /api/v1/loyalty-management/analytics/calculate/    # Calculate analytics for date range
```

### Analytics Data Endpoints
```
GET    /api/v1/loyalty-management/analytics/points_trend/       # Points trend over time
GET    /api/v1/loyalty-management/analytics/top_redemptions/    # Top redemption items
GET    /api/v1/loyalty-management/analytics/tier_distribution/  # Tier distribution
GET    /api/v1/loyalty-management/analytics/engagement_stats/   # Engagement statistics
```

### Dashboard Widgets
```
GET    /api/v1/loyalty-management/dashboard-widgets/      # List widgets
POST   /api/v1/loyalty-management/dashboard-widgets/      # Create widget (admin)
GET    /api/v1/loyalty-management/dashboard-widgets/{id}/ # Retrieve
PUT    /api/v1/loyalty-management/dashboard-widgets/{id}/ # Update (admin)
DELETE /api/v1/loyalty-management/dashboard-widgets/{id}/ # Delete (admin)
```

## API Usage Examples

### Calculate Analytics
```json
POST /api/v1/loyalty-management/analytics/calculate/
{
  "date_from": "2024-01-01",
  "date_to": "2024-01-31"
}

Response:
{
  "id": 1,
  "website": 1,
  "date_from": "2024-01-01",
  "date_to": "2024-01-31",
  "total_active_clients": 1250,
  "total_points_issued": 45000,
  "total_points_redeemed": 18000,
  "total_points_balance": 270000,
  "total_redemptions": 450,
  "total_redemption_value": 18000,
  "most_popular_item": 5,
  "most_popular_item_name": "$10 Discount Code",
  "bronze_count": 800,
  "silver_count": 300,
  "gold_count": 120,
  "platinum_count": 30,
  "active_redemptions_ratio": 36.00,
  "average_points_per_client": 216.00
}
```

### Get Points Trend
```json
GET /api/v1/loyalty-management/analytics/points_trend/?days=30

Response:
[
  {
    "date": "2024-01-01",
    "issued": 1500,
    "redeemed": 600,
    "balance": 900
  },
  {
    "date": "2024-01-02",
    "issued": 2000,
    "redeemed": 500,
    "balance": 2400
  },
  ...
]
```

### Get Top Redemptions
```json
GET /api/v1/loyalty-management/analytics/top_redemptions/?limit=10

Response:
[
  {
    "id": 5,
    "name": "$10 Discount Code",
    "points_required": 1000,
    "redemption_count": 250,
    "category": "Discounts"
  },
  {
    "id": 3,
    "name": "$5 Wallet Credit",
    "points_required": 500,
    "redemption_count": 180,
    "category": "Cash"
  },
  ...
]
```

### Get Tier Distribution
```json
GET /api/v1/loyalty-management/analytics/tier_distribution/

Response:
[
  {
    "tier_name": "Bronze",
    "count": 800,
    "threshold": 0,
    "percentage": 64.00
  },
  {
    "tier_name": "Silver",
    "count": 300,
    "threshold": 1000,
    "percentage": 24.00
  },
  {
    "tier_name": "Gold",
    "count": 120,
    "threshold": 5000,
    "percentage": 9.60
  },
  {
    "tier_name": "Platinum",
    "count": 30,
    "threshold": 10000,
    "percentage": 2.40
  }
]
```

### Get Engagement Stats
```json
GET /api/v1/loyalty-management/analytics/engagement_stats/?days=30

Response:
{
  "total_clients": 2000,
  "active_clients": 1250,
  "clients_with_redemptions": 450,
  "clients_with_transactions": 800,
  "engagement_rate": 40.00,
  "redemption_rate": 36.00
}
```

## Widget Types

1. **Points Issued Over Time**: Line chart showing points issued daily
2. **Redemptions Trend**: Bar/line chart of redemption frequency
3. **Loyalty Tier Distribution**: Pie/bar chart of tier breakdown
4. **Top Redemption Items**: Table/chart of most popular items
5. **Client Engagement Rate**: Metric card with percentage
6. **Points Balance**: Total outstanding points metric
7. **Points to Wallet Conversion**: Conversion rate and volume

## Models

### LoyaltyAnalytics
- Aggregated analytics snapshot for date range
- Calculated periodically (via scheduled tasks)
- Stores pre-computed metrics for performance
- Unique per website/date range combination

### DashboardWidget
- Configurable dashboard components
- Widget type selection
- Position ordering
- Visibility toggle
- Custom configuration (JSON) for chart types, date ranges, etc.

## Service Layer

### LoyaltyAnalyticsService

#### Methods:
- `calculate_analytics(website, date_from, date_to)`: Calculate and store analytics
- `get_points_trend(website, days)`: Get points trend data
- `get_top_redemption_items(website, limit)`: Get most popular items
- `get_tier_distribution(website)`: Get tier breakdown
- `get_client_engagement_stats(website, days)`: Get engagement metrics

## Scheduled Updates

Analytics can be calculated via:
1. **Manual Trigger**: Admin calls `calculate` endpoint
2. **Scheduled Task**: Celery Beat task runs daily/weekly
3. **On-Demand**: Real-time calculation via API

## Performance Considerations

- Analytics snapshots stored in database for quick retrieval
- Pre-computed aggregations reduce query load
- Date range-based snapshots allow historical analysis
- Widgets can cache data with TTL

## Frontend Integration

### Dashboard Layout Example
```javascript
// Fetch widgets
const widgets = await fetch('/api/v1/loyalty-management/dashboard-widgets/');

// Fetch analytics data for each widget
widgets.forEach(async widget => {
  switch(widget.widget_type) {
    case 'points_issued':
      const trend = await fetch('/api/v1/loyalty-management/analytics/points_trend/?days=30');
      renderPointsChart(trend);
      break;
    case 'tier_distribution':
      const tiers = await fetch('/api/v1/loyalty-management/analytics/tier_distribution/');
      renderTierChart(tiers);
      break;
    // ... other widget types
  }
});
```

## Use Cases

1. **Program Performance**: Track overall loyalty program health
2. **Client Segmentation**: Understand tier distribution
3. **Redemption Optimization**: Identify popular items for inventory
4. **Engagement Analysis**: Measure client participation
5. **Forecasting**: Predict redemption patterns
6. **ROI Calculation**: Measure program effectiveness
7. **Campaign Tracking**: Monitor impact of loyalty campaigns

