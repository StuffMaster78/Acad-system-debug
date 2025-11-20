# Admin/Superadmin Dashboard - Untouched Areas

## Overview
This document outlines areas that haven't been implemented in the admin/superadmin dashboard frontend, even though backend APIs may exist.

---

## 🚨 Critical Missing Features

### 1. **Dispute Management Dashboard** ❌
**Backend Status**: ✅ Exists (`DisputeViewSet`, `DisputeService`)
**Frontend Status**: ❌ No Vue component

**What's Missing**:
- Dispute list view with filtering (status, order, raised_by)
- Dispute detail view with resolution workflow
- Dispute resolution interface (approve/reject/mediate)
- Dispute statistics dashboard
- Dispute timeline/history view
- Bulk dispute actions

**Backend Endpoints Available**:
- `GET /api/v1/orders/disputes/` - List disputes
- `POST /api/v1/orders/disputes/` - Create dispute
- `GET /api/v1/orders/disputes/{id}/` - Get dispute details
- `POST /api/v1/orders/disputes/{id}/resolve/` - Resolve dispute

**Priority**: 🔴 HIGH - Critical for operations

---

### 2. **Review Moderation Dashboard** ❌
**Backend Status**: 🟡 Partial (`ReviewModerationService` exists, but no ViewSet)
**Frontend Status**: ❌ No Vue component

**What's Missing**:
- Review moderation queue (pending reviews)
- Review approval/rejection interface
- Review flagging and shadowing
- Review analytics dashboard
- Review spam detection alerts
- Review aggregation and display management

**Backend Status**:
- `ReviewModerationService` exists but no API endpoint
- Review ViewSets exist but no moderation actions

**Priority**: 🔴 HIGH - Needed for content quality

---

### 3. **Refund Management Dashboard** ❌
**Backend Status**: ✅ Exists (`RefundViewSet`)
**Frontend Status**: ❌ No Vue component

**What's Missing**:
- Refund request list with filtering
- Refund approval/rejection workflow
- Refund processing interface
- Refund statistics and analytics
- Refund history tracking
- Automated refund processing rules

**Backend Endpoints Available**:
- `GET /api/v1/refunds/` - List refunds
- `POST /api/v1/refunds/` - Create refund
- `GET /api/v1/refunds/{id}/` - Get refund details
- `POST /api/v1/refunds/{id}/approve/` - Approve refund
- `POST /api/v1/refunds/{id}/reject/` - Reject refund

**Priority**: 🔴 HIGH - Critical for financial operations

---

### 4. **Fines Management Dashboard** ❌
**Backend Status**: 🟡 Partial (Models exist, limited ViewSet)
**Frontend Status**: ❌ No Vue component

**What's Missing**:
- Fine list view with filtering
- Fine calculation automation interface
- Fine appeal management
- Fine payment tracking
- Fine analytics dashboard
- Fine policy management UI
- Fine waiver/void interface

**Backend Status**:
- Fine models exist
- FinePolicy model exists
- FineAppeal model exists
- Limited ViewSet (needs enhancement)

**Priority**: 🟡 MEDIUM - Important for writer management

---

### 5. **Order Management Dashboard** ❌
**Backend Status**: ✅ Exists (`OrderViewSet`)
**Frontend Status**: ❌ No dedicated admin order management view

**What's Missing**:
- Admin order list with advanced filtering
- Order assignment interface
- Order status management
- Order editing/override capabilities
- Order bulk actions
- Order analytics dashboard
- Order timeline/history view

**Backend Endpoints Available**:
- `GET /api/v1/orders/` - List orders
- `GET /api/v1/orders/{id}/` - Get order details
- `PATCH /api/v1/orders/{id}/` - Update order
- Various order action endpoints

**Note**: There's a general order list view, but no admin-specific order management interface

**Priority**: 🔴 HIGH - Core functionality

---

### 6. **Special Orders Management Dashboard** ❌
**Backend Status**: ✅ Exists (`SpecialOrderViewSet`)
**Frontend Status**: ❌ No Vue component

**What's Missing**:
- Special order list view with filtering (status, type, client, writer)
- Special order approval workflow interface
- Estimated order cost approval interface
- Installment payment management
- Payment override controls
- File unlock controls
- Special order analytics dashboard
- Predefined special order config management
- Estimated special order settings management
- Writer bonus management

**Backend Endpoints Available**:
- `GET /api/v1/special-orders/` - List special orders
- `POST /api/v1/special-orders/` - Create special order
- `GET /api/v1/special-orders/{id}/` - Get order details
- `POST /api/v1/special-orders/{id}/approve/` - Approve order (admin)
- `POST /api/v1/special-orders/{id}/override_payment/` - Override payment
- `POST /api/v1/special-orders/{id}/complete_order/` - Complete order
- `GET /api/v1/special-orders/installment-payments/` - List installments
- `POST /api/v1/special-orders/installment-payments/{id}/pay_installment/` - Pay installment
- `GET /api/v1/special-orders/predefined-special-order-configs/` - List configs
- `GET /api/v1/special-orders/estimated-special-order-settings/` - Get settings

**Key Features Needed**:
- Approval queue for `awaiting_approval` status orders
- Cost estimation interface for `estimated` type orders
- Installment tracking and payment management
- Admin override controls (payment, file access)
- Predefined order type configuration
- Deposit percentage settings

**Priority**: 🔴 HIGH - Critical for special order operations

---

### 7. **Class Management Dashboard** ❌
**Backend Status**: ✅ Exists (`ClassBundleViewSet`, `ClassPurchaseViewSet`, etc.)
**Frontend Status**: ❌ No Vue component

**What's Missing**:
- Class bundle list view with filtering (status, client, writer, website)
- Admin manual bundle creation interface
- Bundle configuration management
- Installment configuration interface
- Deposit payment management
- Class bundle file management
- Class bundle communication/threads management
- Class bundle ticket management
- Class bundle analytics dashboard
- Class bundle config management (levels, durations, bundle sizes)

**Backend Endpoints Available**:
- `GET /api/v1/class-management/class-bundles/` - List bundles
- `POST /api/v1/class-management/class-bundles/` - Create bundle
- `POST /api/v1/class-management/class-bundles/create_manual/` - Admin create bundle
- `GET /api/v1/class-management/class-bundles/{id}/` - Get bundle details
- `POST /api/v1/class-management/class-bundles/{id}/pay_deposit/` - Pay deposit
- `POST /api/v1/class-management/class-bundles/{id}/configure_installments/` - Configure installments
- `POST /api/v1/class-management/class-bundles/{id}/create_thread/` - Create communication thread
- `POST /api/v1/class-management/class-bundles/{id}/create_ticket/` - Create support ticket
- `GET /api/v1/class-management/class-purchases/` - List purchases
- `GET /api/v1/class-management/class-installments/` - List installments
- `GET /api/v1/class-management/class-bundle-configs/` - List bundle configs

**Key Features Needed**:
- Admin manual bundle creation with custom pricing
- Installment configuration (count, intervals, amounts)
- Deposit payment processing
- Bundle assignment to writers
- Bundle file upload/download management
- Bundle communication threads
- Bundle support tickets
- Bundle config management (pricing tiers, levels, durations)

**Priority**: 🔴 HIGH - Critical for class/bundle operations

---

## 📊 Analytics & Reporting (Missing)

### 8. **Advanced Analytics Dashboard** ❌
**Backend Status**: 🟡 Partial (some metrics exist)
**Frontend Status**: ❌ No comprehensive analytics view

**What's Missing**:
- Revenue analytics (trends, forecasts)
- User growth analytics
- Writer performance analytics
- Client lifetime value analytics
- Service popularity analytics
- Conversion funnel analytics
- Custom date range reports
- Export functionality (CSV/PDF)

**Existing Backend**:
- `DashboardMetricsService` has basic metrics
- Loyalty analytics exist
- Discount analytics exist
- No comprehensive analytics aggregation

**Priority**: 🟡 MEDIUM - Important for business insights

---

### 9. **Activity Logs Dashboard** ❌
**Backend Status**: ✅ Exists (`AdminActivityLogViewSet`)
**Frontend Status**: ❌ No dedicated activity logs view

**What's Missing**:
- Activity log viewer with filtering
- Activity search functionality
- Activity analytics/aggregation
- Real-time activity feed
- Activity export functionality
- User activity timeline
- Activity dashboard widgets

**Backend Endpoints Available**:
- `GET /api/v1/admin-management/activity-logs/` - List activity logs

**Note**: There's a basic activity view, but no comprehensive dashboard

**Priority**: 🟡 MEDIUM - Important for audit trails

---

## 🔧 System Management (Missing)

### 10. **Superadmin-Specific Features** ❌
**Backend Status**: 🟡 Partial (`SuperadminDashboardViewSet` exists but basic)
**Frontend Status**: ❌ No superadmin-specific views

**What's Missing**:
- Multi-tenant management interface
- Cross-tenant analytics
- System-wide configuration management
- Tenant creation/management
- System health monitoring
- Cross-tenant bulk operations
- Superadmin audit trail viewer

**Backend Status**:
- `SuperadminDashboardViewSet` exists but is basic
- No cross-tenant operations API
- No system configuration API

**Priority**: 🟡 MEDIUM - Important for superadmin operations

---

### 11. **Support Ticket Management** ❌
**Backend Status**: ✅ Exists (`TicketViewSet`)
**Frontend Status**: ❌ No admin ticket management view

**What's Missing**:
- Admin ticket queue
- Ticket assignment interface
- SLA monitoring dashboard
- Support workload balancing
- Ticket escalation management
- Support performance metrics
- Ticket analytics

**Backend Endpoints Available**:
- `GET /api/v1/support-management/tickets/` - List tickets
- Various ticket management endpoints

**Note**: There's a general ticket view, but no admin-specific management interface

**Priority**: 🟡 MEDIUM - Important for support operations

---

## 📈 Business Intelligence (Missing)

### 12. **Pricing Analytics Dashboard** ❌
**Backend Status**: ❌ No dedicated pricing analytics API
**Frontend Status**: ❌ No pricing analytics view

**What's Missing**:
- Pricing history tracking
- Pricing change impact analysis
- Revenue impact of pricing changes
- Competitive pricing analysis
- Pricing optimization suggestions
- Dynamic pricing calculator
- Pricing configuration templates

**Priority**: 🟢 LOW - Nice to have

---

### 13. **Discount Analytics Dashboard** ❌
**Backend Status**: ✅ Exists (`DiscountAnalyticsView`)
**Frontend Status**: ❌ No discount analytics view

**What's Missing**:
- Discount usage statistics
- Discount effectiveness metrics
- Revenue impact of discounts
- Discount code performance
- Discount expiration tracking
- Discount optimization suggestions

**Backend Endpoints Available**:
- `GET /api/v1/discounts/analytics/` - Discount analytics

**Priority**: 🟡 MEDIUM - Important for marketing

---

### 14. **Writer Performance Analytics** ❌
**Backend Status**: ✅ Exists (Writer performance models)
**Frontend Status**: ❌ No comprehensive writer analytics view

**What's Missing**:
- Writer performance dashboard
- Writer ranking/leaderboard
- Writer quality metrics
- Writer earnings analytics
- Writer completion rates
- Writer review scores
- Writer performance trends

**Backend Status**:
- Writer performance models exist
- Limited analytics endpoints

**Priority**: 🟡 MEDIUM - Important for writer management

---

## 🎯 Content Management (Missing)

### 15. **Review Aggregation & Display** ❌
**Backend Status**: ❌ No aggregation service
**Frontend Status**: ❌ No review display management

**What's Missing**:
- Review aggregation service
- Review display rules management
- Review sorting/filtering configuration
- Review moderation queue
- Review display preview

**Priority**: 🟡 MEDIUM - Important for reputation management

---

## 📋 Summary by Priority

### 🔴 HIGH PRIORITY (Critical for Operations)
1. **Dispute Management Dashboard** - No frontend component
2. **Refund Management Dashboard** - No frontend component
3. **Order Management Dashboard** - No admin-specific interface
4. **Review Moderation Dashboard** - No frontend component
5. **Special Orders Management Dashboard** - No frontend component
6. **Class Management Dashboard** - No frontend component

### 🟡 MEDIUM PRIORITY (Important Features)
7. **Fines Management Dashboard** - Needs frontend + backend enhancement
8. **Advanced Analytics Dashboard** - Needs comprehensive view
9. **Activity Logs Dashboard** - Needs enhanced interface
10. **Superadmin-Specific Features** - Needs multi-tenant management
11. **Support Ticket Management** - Needs admin-specific interface
12. **Discount Analytics Dashboard** - Backend exists, needs frontend
13. **Writer Performance Analytics** - Needs comprehensive dashboard
14. **Review Aggregation & Display** - Needs service + frontend

### 🟢 LOW PRIORITY (Nice to Have)
15. **Pricing Analytics Dashboard** - Needs backend + frontend

---

## 📝 Implementation Notes

### Backend APIs That Exist But No Frontend:
- `/api/v1/orders/disputes/` - Dispute management
- `/api/v1/refunds/` - Refund management
- `/api/v1/admin-management/activity-logs/` - Activity logs
- `/api/v1/discounts/analytics/` - Discount analytics
- `/api/v1/support-management/tickets/` - Support tickets
- `/api/v1/special-orders/` - Special orders management
- `/api/v1/class-management/class-bundles/` - Class bundle management

### Backend Services That Need API Endpoints:
- `ReviewModerationService` - Needs ViewSet/API
- Fine management - Needs enhanced ViewSet
- Pricing analytics - Needs new service + API
- Writer performance analytics - Needs aggregation API

### Frontend Routes to Add:
```javascript
// Missing routes in router/index.js
{
  path: 'admin/disputes',
  name: 'DisputeManagement',
  component: () => import('@/views/admin/DisputeManagement.vue'),
  meta: { roles: ['admin', 'superadmin'] }
},
{
  path: 'admin/refunds',
  name: 'RefundManagement',
  component: () => import('@/views/admin/RefundManagement.vue'),
  meta: { roles: ['admin', 'superadmin'] }
},
{
  path: 'admin/reviews',
  name: 'ReviewModeration',
  component: () => import('@/views/admin/ReviewModeration.vue'),
  meta: { roles: ['admin', 'superadmin'] }
},
{
  path: 'admin/fines',
  name: 'FineManagement',
  component: () => import('@/views/admin/FineManagement.vue'),
  meta: { roles: ['admin', 'superadmin'] }
},
{
  path: 'admin/analytics',
  name: 'AnalyticsDashboard',
  component: () => import('@/views/admin/AnalyticsDashboard.vue'),
  meta: { roles: ['admin', 'superadmin'] }
},
{
  path: 'admin/orders',
  name: 'OrderManagement',
  component: () => import('@/views/admin/OrderManagement.vue'),
  meta: { roles: ['admin', 'superadmin'] }
},
{
  path: 'admin/special-orders',
  name: 'SpecialOrderManagement',
  component: () => import('@/views/admin/SpecialOrderManagement.vue'),
  meta: { roles: ['admin', 'superadmin'] }
},
{
  path: 'admin/class-management',
  name: 'ClassManagement',
  component: () => import('@/views/admin/ClassManagement.vue'),
  meta: { roles: ['admin', 'superadmin'] }
}
```

---

## 🎯 Recommended Implementation Order

1. **Dispute Management** - Critical for operations
2. **Refund Management** - Critical for financial operations
3. **Order Management** - Core functionality
4. **Special Orders Management** - Critical for special order operations
5. **Class Management** - Critical for class/bundle operations
6. **Review Moderation** - Content quality
7. **Fines Management** - Writer management
8. **Analytics Dashboard** - Business intelligence
9. **Activity Logs** - Audit trails
10. **Support Ticket Management** - Support operations
11. **Discount Analytics** - Marketing insights
12. **Writer Performance Analytics** - Writer management
13. **Superadmin Features** - Multi-tenant management
14. **Pricing Analytics** - Business optimization

---

## 📊 Current Coverage

**Implemented Admin Features**:
- ✅ User Management (`UserManagement.vue`)
- ✅ Configuration Management (`ConfigManagement.vue`)
- ✅ Email Management (`EmailManagement.vue`)
- ✅ Blog Management (`BlogManagement.vue`)
- ✅ SEO Pages Management (`SEOPagesManagement.vue`)
- ✅ Wallet Management (`WalletManagement.vue`)
- ✅ Website Management (`WebsiteManagement.vue`)
- ✅ Payment Logs (`PaymentLogs.vue`)
- ✅ Writer Payments (`WriterPayments.vue`)

**Missing Admin Features**:
- ❌ Dispute Management
- ❌ Refund Management
- ❌ Review Moderation
- ❌ Fine Management
- ❌ Order Management (admin-specific)
- ❌ Special Orders Management
- ❌ Class Management
- ❌ Support Ticket Management (admin-specific)
- ❌ Analytics Dashboard
- ❌ Activity Logs Dashboard
- ❌ Discount Analytics
- ❌ Writer Performance Analytics
- ❌ Superadmin Multi-tenant Management

---

**Last Updated**: Based on codebase analysis as of current date

