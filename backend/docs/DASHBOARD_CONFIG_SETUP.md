# Dashboard Configuration System

## Overview
The dashboard now uses a database-driven configuration system that allows admins to:
- Configure card colors, icons, labels, and content from the database
- Set role-based access control for cards
- Customize fonts and typography
- Avoid redundancy by filtering cards based on user roles

## Models

### DashboardCardConfig
Stores configuration for individual dashboard cards:
- `card_key`: Unique identifier (e.g., 'total_orders', 'total_revenue')
- `title`: Card title/label
- `icon`: Emoji or icon identifier
- `color`: Card color theme (blue, green, purple, orange, red, pink, indigo, teal)
- `data_source`: API endpoint or data path (e.g., 'dashboardData.total_orders')
- `data_type`: Type of data (number, currency, percentage, text)
- `allowed_roles`: JSON array of roles that can see this card
- `website`: Optional website-specific card (null = all websites)
- `position`: Display order
- `is_active`: Whether card is active
- `badge_text`: Footer badge text (e.g., 'All time', 'Last 30 days')

### DashboardFontConfig
Stores font configuration:
- `font_family`: CSS font-family value
- `font_url`: URL to load font from
- `base_font_size`: Base font size
- `card_value_font_size`: Card value font size
- `card_label_font_size`: Card label font size
- `website`: Optional website-specific config

## API Endpoint

### GET `/api/v1/dashboard-config/`
Returns dashboard configuration for the current user's role.

**Response:**
```json
{
  "role": "admin",
  "cards": [
    {
      "key": "total_orders",
      "title": "Total Orders",
      "description": "All time orders",
      "icon": "📦",
      "color": "blue",
      "data_source": "dashboardData.total_orders",
      "data_type": "number",
      "badge_text": "All time",
      "position": 0,
      "config": {}
    }
  ],
  "font_config": {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "font_url": "",
    "base_font_size": "16px",
    "card_value_font_size": "clamp(24px, 3vw, 32px)",
    "card_label_font_size": "13px"
  }
}
```

## Admin Interface

Access the admin panel to manage dashboard cards:
1. Go to `/admin/core/dashboardcardconfig/`
2. Create/edit cards with:
   - Card information (key, title, icon, color, position)
   - Data configuration (source, type, badge)
   - Access control (allowed roles, website)

## CSS Overflow Fixes

The CSS has been updated to prevent currency value overflow:
- Reduced font sizes for money values: `clamp(16px, 1.8vw, 22px)`
- Added `overflow-wrap: anywhere` for long amounts
- Set `min-width: 0` on grid items to prevent overflow
- Better responsive sizing for large numbers

## Next Steps

1. **Create Migration**: Run `makemigrations` and `migrate` to create the models
2. **Populate Initial Data**: Create card configurations for each role
3. **Update Frontend**: Modify Dashboard.vue to fetch and render cards from the API
4. **Test**: Verify cards display correctly and role filtering works

## Example Card Configuration

```python
DashboardCardConfig.objects.create(
    card_key='total_revenue',
    title='Total Revenue',
    icon='💰',
    color='green',
    data_source='dashboardData.total_revenue',
    data_type='currency',
    allowed_roles=['admin', 'superadmin'],
    badge_text='All time',
    position=2,
    is_active=True
)
```

