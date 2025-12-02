# Frontend Development Roadmap

## ✅ Completed (Ready for Frontend)

### Backend Implementation - 100% Complete
- ✅ All models, migrations, serializers, ViewSets
- ✅ All API endpoints registered and tested
- ✅ All API clients created in `frontend/src/api/`

### API Clients Available
All these API clients are ready to use in Vue components:

1. **Login Alerts** (`loginAlertsAPI`)
   - `getPreferences()`, `updatePreferences()`, `createPreferences()`

2. **Order Drafts** (`orderDraftsAPI`)
   - `list()`, `get()`, `create()`, `update()`, `delete()`, `convertToOrder()`

3. **Order Presets** (`orderPresetsAPI`)
   - `list()`, `get()`, `create()`, `update()`, `delete()`, `apply()`

4. **Analytics** (`analyticsAPI`)
   - `client.*`, `writer.*`, `class.*` with various methods

5. **Enhanced Disputes** (`enhancedDisputesAPI`)
   - `list()`, `get()`, `create()`, `update()`, `escalate()`, `resolve()`, `close()`
   - `messages.list()`, `messages.create()`

6. **Writer Capacity** (`writerCapacityAPI`)
   - `list()`, `get()`, `create()`, `update()`
   - `editor.list()`, `editor.get()`, `editor.create()`, `editor.update()`

7. **Tenant Features** (`tenantFeaturesAPI`)
   - `branding.*` - Branding management
   - `toggles.*` - Feature toggle management

8. **Holidays** (`holidaysAPI`)
   - `specialDays.*` - Special days management
   - `reminders.*` - Reminder management
   - `campaigns.*` - Campaign viewing

## 🎯 Frontend Components to Build

### Priority 1: High-Impact Features

#### 1. Login Alerts Settings
**Location**: `frontend/src/views/account/Settings.vue` or new component
**Features**:
- Toggle switches for:
  - Notify on new login
  - Notify on new device
  - Notify on new location
  - Email notifications
  - Push notifications
- Save preferences
- Show current settings

**API**: `loginAlertsAPI`

#### 2. Order Drafts Management
**Location**: `frontend/src/views/orders/OrderDrafts.vue` (new)
**Features**:
- List all drafts
- Create new draft
- Edit draft
- Convert draft to order
- Delete draft
- Filter by status (draft, quote)
- Search drafts

**API**: `orderDraftsAPI`

#### 3. Order Presets Management
**Location**: `frontend/src/views/orders/OrderPresets.vue` (new)
**Features**:
- List all presets
- Create preset from existing order
- Edit preset
- Apply preset to create new order/draft
- Set as default preset
- Delete preset

**API**: `orderPresetsAPI`

#### 4. Analytics Dashboards

**Client Analytics Dashboard**
- Location: `frontend/src/views/dashboard/components/ClientAnalytics.vue`
- Features:
  - Spend over time chart
  - On-time delivery percentage
  - Revision rates
  - Writer performance metrics
  - Period selector (last 30/60/90 days)

**Writer Analytics Dashboard**
- Location: `frontend/src/views/dashboard/components/WriterAnalytics.vue`
- Features:
  - Effective hourly rate
  - Earnings vs time chart
  - Revision/approval rates
  - Quality scores over time
  - Period selector

**Class Analytics Dashboard**
- Location: `frontend/src/views/admin/ClassAnalytics.vue` (new)
- Features:
  - Attendance/completion rates
  - Performance per group
  - Exportable reports
  - Generate performance reports

**API**: `analyticsAPI`

#### 5. Enhanced Disputes
**Location**: `frontend/src/views/support/Disputes.vue` (new or update existing)
**Features**:
- List disputes with filters (status, priority)
- Create dispute
- View dispute details
- Escalate dispute
- Resolve dispute
- Close dispute
- Dispute messages thread
- Send messages in dispute

**API**: `enhancedDisputesAPI`

#### 6. Writer Capacity Management
**Location**: `frontend/src/views/writers/Capacity.vue` (new)
**Features**:
- Set max active orders
- Set availability status
- Add blackout dates
- Set preferred subjects/types of work
- View current capacity
- Editor workload management (for editors)

**API**: `writerCapacityAPI`

#### 7. Tenant Branding & Features
**Location**: `frontend/src/views/superadmin/TenantSettings.vue` (new)
**Features**:
- Email subject prefix
- Reply-to address
- Custom CSS/JS
- Feature toggles (magic link, 2FA required, etc.)
- Per-tenant configuration

**API**: `tenantFeaturesAPI`

#### 8. Holiday Management Dashboard
**Location**: `frontend/src/views/admin/HolidayManagement.vue` (new)
**Features**:
- Calendar view of upcoming special days
- List all special days
- Create/edit special days
- View pending reminders
- Generate discounts
- View discount campaigns
- Country filter
- Event type filter

**API**: `holidaysAPI`

### Priority 2: Integration Points

#### 1. Order Creation Flow
- Add "Save as Draft" button
- Add "Use Preset" option
- Show draft conversion option

#### 2. Order Detail Page
- Show related drafts
- Show applied preset
- Link to create preset from order

#### 3. Discounts Page
- Show holiday-generated discounts
- Filter by holiday campaign
- Show auto-generated badge

#### 4. Admin Dashboard
- Holiday reminders widget
- Upcoming special days
- Pending reminders count
- Quick actions (generate discount, send broadcast)

#### 5. Broadcast Messages
- Integrate with holiday reminders
- Use broadcast message templates
- Auto-populate from special day

## 📁 Suggested File Structure

```
frontend/src/
├── views/
│   ├── account/
│   │   └── LoginAlertsSettings.vue (new)
│   ├── orders/
│   │   ├── OrderDrafts.vue (new)
│   │   ├── OrderPresets.vue (new)
│   │   └── OrderDetail.vue (update - add drafts/presets)
│   ├── dashboard/
│   │   └── components/
│   │       ├── ClientAnalytics.vue (new)
│   │       └── WriterAnalytics.vue (new)
│   ├── admin/
│   │   ├── HolidayManagement.vue (new)
│   │   └── ClassAnalytics.vue (new)
│   ├── support/
│   │   └── Disputes.vue (new or update)
│   ├── writers/
│   │   └── Capacity.vue (new)
│   └── superadmin/
│       └── TenantSettings.vue (new)
├── components/
│   ├── holidays/
│   │   ├── SpecialDayCard.vue (new)
│   │   ├── ReminderCard.vue (new)
│   │   └── HolidayCalendar.vue (new)
│   ├── analytics/
│   │   ├── AnalyticsChart.vue (new)
│   │   └── MetricsCard.vue (new)
│   └── disputes/
│       ├── DisputeCard.vue (new)
│       └── DisputeMessageThread.vue (new)
└── api/
    └── (all API clients already created ✅)
```

## 🎨 Component Patterns to Follow

### 1. List/Detail Pattern
- Use `EnhancedDataTable` for lists
- Use tabs for detail views
- Follow existing order detail page patterns

### 2. Form Patterns
- Use `FormField` component
- Use `ConfirmationDialog` for destructive actions
- Follow existing form validation patterns

### 3. Dashboard Patterns
- Use cards for metrics
- Use charts for visualizations
- Follow existing dashboard layout

### 4. Modal Patterns
- Use `Modal` component
- Use `NewMessageModal` pattern for forms
- Follow existing modal patterns

## 🔗 Integration Points

### Existing Components to Update

1. **Order Creation** (`OrderCreate.vue`)
   - Add "Save as Draft" button
   - Add "Use Preset" dropdown
   - Add "Create Preset" option

2. **Order Detail** (`OrderDetail.vue`)
   - Show draft conversion status
   - Show applied preset
   - Add "Create Preset from Order" action

3. **Discounts Page** (`DiscountManagement.vue`)
   - Show holiday campaign badge
   - Filter by holiday
   - Show auto-generated indicator

4. **Admin Dashboard** (`Dashboard.vue`)
   - Add holiday reminders widget
   - Show upcoming special days
   - Quick actions for reminders

5. **Settings Page** (`Settings.vue`)
   - Add Login Alerts tab
   - Show current preferences
   - Toggle switches

## 📋 Development Checklist

### Phase 1: Core Features
- [ ] Login Alerts Settings Component
- [ ] Order Drafts Management
- [ ] Order Presets Management
- [ ] Holiday Management Dashboard

### Phase 2: Analytics
- [ ] Client Analytics Dashboard
- [ ] Writer Analytics Dashboard
- [ ] Class Analytics Dashboard

### Phase 3: Support & Management
- [ ] Enhanced Disputes Interface
- [ ] Writer Capacity Management
- [ ] Tenant Branding & Features

### Phase 4: Integration
- [ ] Integrate drafts into order creation
- [ ] Integrate presets into order creation
- [ ] Integrate holiday reminders into admin dashboard
- [ ] Integrate analytics into existing dashboards

## 🚀 Quick Start Guide

### 1. Import API Clients
```javascript
import { 
  loginAlertsAPI, 
  orderDraftsAPI, 
  holidaysAPI,
  analyticsAPI 
} from '@/api'
```

### 2. Example Component Structure
```vue
<template>
  <div class="holiday-management">
    <h1>Holiday Management</h1>
    <EnhancedDataTable
      :data="specialDays"
      :columns="columns"
      @row-click="handleRowClick"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { holidaysAPI } from '@/api'

const specialDays = ref([])

onMounted(async () => {
  const response = await holidaysAPI.specialDays.list()
  specialDays.value = response.data
})
</script>
```

## 📚 Reference Files

### Existing Components to Reference
- `frontend/src/views/orders/OrderDetail.vue` - Complex detail page
- `frontend/src/views/admin/OrderManagement.vue` - List/table pattern
- `frontend/src/components/common/Modal.vue` - Modal pattern
- `frontend/src/components/common/EnhancedDataTable.vue` - Table pattern
- `frontend/src/views/dashboard/Dashboard.vue` - Dashboard layout

### API Usage Examples
- `frontend/src/api/orders.js` - Order API usage
- `frontend/src/api/admin-management.js` - Admin API usage
- `frontend/src/views/orders/OrderList.vue` - API integration example

## 🎯 Priority Order

1. **Holiday Management** - High business impact, admin-facing
2. **Order Drafts & Presets** - Client-facing, improves UX
3. **Analytics Dashboards** - User transparency, engagement
4. **Login Alerts** - Security feature, user-facing
5. **Enhanced Disputes** - Support workflow improvement
6. **Writer Capacity** - Writer experience improvement
7. **Tenant Features** - Superadmin configuration

## 📝 Notes

- All API clients are ready and tested
- Backend is fully functional
- Follow existing component patterns
- Use existing UI components (Modal, DataTable, FormField, etc.)
- All endpoints are accessible and documented

## 🎊 Status

**Backend**: ✅ 100% Complete
**API Clients**: ✅ 100% Complete
**Frontend Components**: ⏳ Ready to Start

Good luck with the frontend development! 🚀

