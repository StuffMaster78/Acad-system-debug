# Tip Management User Guide

## Overview

The Tip Management system allows administrators to track, analyze, and manage tips given to writers. This guide provides step-by-step instructions for using the Tip Management dashboard and understanding the data presented.

---

## Accessing Tip Management

1. **Login** to the admin panel with admin or superadmin credentials
2. **Navigate** to the Tip Management section in the admin dashboard
3. **URL**: `/api/v1/admin-management/tips/`

**Note**: Only users with admin or superadmin roles can access Tip Management.

---

## Dashboard Overview

The Tip Management dashboard provides a comprehensive overview of all tip-related statistics.

### Key Metrics

The dashboard displays several key metrics:

#### Summary Statistics
- **Total Tips**: Total number of tips ever given
- **Total Tip Amount**: Sum of all tip amounts
- **Total Writer Earnings**: Total amount earned by writers
- **Total Platform Profit**: Total amount earned by the platform
- **Average Tip Amount**: Average tip amount across all tips
- **Average Writer Percentage**: Average percentage of tips going to writers

#### Recent Summary (Last N Days)
- **Days**: Number of days for recent statistics (default: 30, range: 1-365)
- **Total Tips**: Number of tips in the period
- **Total Tip Amount**: Sum of tip amounts in the period
- **Total Writer Earnings**: Sum of writer earnings in the period
- **Total Platform Profit**: Sum of platform profit in the period

#### Payment Status
- **Completed**: Tips with successfully completed payments
- **Pending**: Tips awaiting payment processing
- **Processing**: Tips currently being processed
- **Failed**: Tips with failed payments

### Breakdowns

#### Tip Type Breakdown
Shows statistics by tip type:
- **Direct**: Tips given directly to writers (not tied to orders or classes)
- **Order**: Tips given for specific orders
- **Class**: Tips given for class bundles or express classes

#### Payment Status Breakdown
Detailed breakdown showing count and total amount for each payment status.

#### Writer Level Breakdown
Shows statistics by writer level (e.g., Senior, Intermediate, Junior), including:
- Number of tips
- Total tip amount
- Writer earnings
- Platform profit
- Average writer percentage

---

## List Tips

The List Tips page allows you to view and filter individual tips.

### Filtering Options

You can filter tips by:

1. **Tip Type**: `direct`, `order`, or `class`
2. **Payment Status**: `pending`, `processing`, `completed`, or `failed`
3. **Writer ID**: Filter by specific writer
4. **Client ID**: Filter by specific client
5. **Date Range**: 
   - `date_from`: Start date (YYYY-MM-DD)
   - `date_to`: End date (YYYY-MM-DD)

### Pagination

- **Limit**: Number of results per page (default: 50, max: 1000)
- **Offset**: Number of results to skip (default: 0)

### Understanding Tip Details

Each tip entry shows:
- **Tip ID**: Unique identifier
- **Client**: Information about who gave the tip
- **Writer**: Information about who received the tip
- **Tip Type**: Type of tip (direct, order, class)
- **Tip Amount**: Total tip amount
- **Writer Earning**: Amount earned by writer
- **Platform Profit**: Amount earned by platform
- **Writer Percentage**: Percentage of tip going to writer
- **Payment Status**: Current payment status
- **Sent At**: Timestamp when tip was sent
- **Order**: Order information (if applicable)
- **Website**: Website information

### Summary Statistics

The List Tips page also shows summary statistics for the filtered results:
- Total tip amount
- Total writer earnings
- Total platform profit

---

## Analytics

The Analytics page provides detailed insights into tip trends and patterns.

### Time-Based Trends

#### Monthly Trends
Shows tip statistics aggregated by month for the selected period.

#### Weekly Trends
Shows tip statistics aggregated by week for the last 12 weeks.

#### Daily Trends
Shows tip statistics aggregated by day for the last 30 days.

### Breakdowns

#### By Type
Breakdown of tips by type (direct, order, class) with:
- Count
- Total amount
- Writer earnings
- Platform profit
- Average amount

#### By Level
Breakdown of tips by writer level with:
- Tip count
- Total tips
- Writer earnings
- Platform profit
- Average percentage

### Top Performers

#### Top Writers
Lists the top 10 writers by total earnings, showing:
- Writer information
- Tip count
- Total received
- Average tip

#### Top Clients
Lists the top 10 clients by total tips sent, showing:
- Client information
- Tip count
- Total sent

### Date Range

You can adjust the analytics period using the `days` parameter:
- **Default**: 90 days
- **Range**: 1-365 days
- **Note**: Larger date ranges may take longer to load

---

## Earnings

The Earnings page shows detailed earnings breakdown for completed tips only.

### Overall Statistics

- **Total Tips**: Number of completed tips
- **Total Tip Amount**: Sum of completed tip amounts
- **Total Writer Earnings**: Sum of writer earnings from completed tips
- **Total Platform Profit**: Sum of platform profit from completed tips
- **Average Tip Amount**: Average tip amount
- **Average Writer Percentage**: Average writer percentage
- **Platform Profit Percentage**: Platform profit as percentage of total

### Breakdowns

#### By Level
Earnings breakdown by writer level, showing how different writer levels perform.

#### By Type
Earnings breakdown by tip type, showing which types of tips generate the most revenue.

#### Monthly
Monthly earnings breakdown for the last 12 months, useful for tracking trends over time.

### Date Filtering

You can filter earnings by date range:
- **date_from**: Start date (YYYY-MM-DD)
- **date_to**: End date (YYYY-MM-DD)

**Note**: Only completed tips are included in earnings calculations.

---

## Understanding Tip Distribution

### How Tips Are Split

Tips are distributed between writers and the platform based on the writer's level:

1. **Writer Level Percentage**: Each writer level has a configured tip percentage (e.g., Senior: 35%, Intermediate: 30%)
2. **Writer Earning**: `tip_amount × writer_percentage / 100`
3. **Platform Profit**: `tip_amount - writer_earning`

### Example

If a client gives a $100 tip to a Senior writer (35%):
- **Writer Earning**: $100 × 0.35 = $35.00
- **Platform Profit**: $100 - $35.00 = $65.00

### Default Percentage

If a writer doesn't have a level assigned, the default writer percentage is 30%.

---

## Best Practices

### 1. Regular Monitoring
- Check the dashboard regularly to monitor tip trends
- Review payment status to identify any issues
- Monitor failed payments and take appropriate action

### 2. Analytics Review
- Review monthly trends to identify patterns
- Compare writer levels to understand performance
- Track top performers to recognize excellence

### 3. Filtering Tips
- Use date ranges to focus on specific periods
- Filter by payment status to identify issues
- Filter by writer/client for detailed analysis

### 4. Performance Optimization
- Use appropriate date ranges (smaller ranges load faster)
- Limit pagination to reasonable sizes (50-100 records)
- Combine filters to narrow down results

---

## Common Tasks

### Finding Tips for a Specific Writer

1. Go to **List Tips**
2. Enter the writer ID in the `writer_id` filter
3. Optionally add date range or payment status filters
4. Click **Search**

### Analyzing Monthly Trends

1. Go to **Analytics**
2. Set `days` to 365 for full year analysis
3. Review the **Monthly Trends** section
4. Compare months to identify patterns

### Checking Payment Issues

1. Go to **Dashboard**
2. Review the **Payment Status** section
3. Check for high numbers of `pending` or `failed` tips
4. Go to **List Tips** and filter by payment status
5. Investigate individual tips as needed

### Exporting Data

Currently, data export is not available through the UI. Use the API endpoints directly to fetch data programmatically.

---

## Troubleshooting

### Dashboard Not Loading

- **Check Authentication**: Ensure you're logged in with admin/superadmin role
- **Check Permissions**: Verify your user has the required permissions
- **Check Date Range**: Very large date ranges may timeout

### Missing Data

- **Check Website Context**: Admins only see tips for their assigned website
- **Check Date Filters**: Ensure date filters are not excluding data
- **Check Payment Status**: Some views only show completed tips

### Performance Issues

- **Reduce Date Range**: Use smaller date ranges for faster loading
- **Reduce Limit**: Use smaller pagination limits
- **Add Filters**: More specific filters reduce data processing

---

## Tips for Admins

1. **Regular Reviews**: Schedule regular reviews of tip statistics
2. **Identify Patterns**: Use analytics to identify trends and patterns
3. **Recognize Excellence**: Use top performers list to recognize excellent writers
4. **Monitor Issues**: Keep an eye on failed payments and take action
5. **Optimize Performance**: Use appropriate filters and date ranges for faster loading

---

## Support

For issues or questions:
1. Check this guide first
2. Review the API documentation
3. Contact the development team
4. Check system logs for errors

---

## Glossary

- **Tip**: A monetary reward given to a writer
- **Tip Type**: Category of tip (direct, order, class)
- **Writer Earning**: Amount earned by the writer from a tip
- **Platform Profit**: Amount earned by the platform from a tip
- **Writer Percentage**: Percentage of tip going to the writer
- **Payment Status**: Current state of tip payment (pending, processing, completed, failed)
- **Writer Level**: Classification of writer (Senior, Intermediate, Junior, etc.)

---

## Appendix: API Endpoints

For programmatic access, use these endpoints:

- **Dashboard**: `GET /api/v1/admin-management/tips/dashboard/`
- **List Tips**: `GET /api/v1/admin-management/tips/list_tips/`
- **Analytics**: `GET /api/v1/admin-management/tips/analytics/`
- **Earnings**: `GET /api/v1/admin-management/tips/earnings/`

See `TIP_MANAGEMENT_API_DOCUMENTATION.md` for detailed API documentation.

