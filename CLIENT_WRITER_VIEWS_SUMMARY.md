# Client & Writer Views for Special Orders and Express Classes

**Date**: January 9, 2025  
**Status**: Implementation in Progress

---

## Summary

We've identified that clients and writers need dedicated views to manage their special orders and express classes. Currently:
- ✅ Clients can CREATE special orders and express classes
- ❌ Clients cannot VIEW/LIST their special orders and express classes
- ❌ Writers cannot see their assigned special orders and express classes

---

## ✅ **COMPLETED: Client Views**

### 1. ClientSpecialOrders.vue
- **Route**: `/client/special-orders`
- **Features**:
  - List all client's special orders
  - Filter by status (inquiry, awaiting_approval, in_progress, completed)
  - Search by ID or details
  - Stats cards (Total, Awaiting Approval, In Progress, Completed)
  - Click to view details
  - Pagination support

### 2. ClientSpecialOrderDetail.vue
- **Route**: `/client/special-orders/:id`
- **Features**:
  - Overview tab (order info, inquiry details, financial info, writer info)
  - Messages tab (integrated with SimplifiedOrderMessages)
  - Files tab (list and download files)
  - Status badges and labels
  - Breadcrumb navigation

### 3. ClientExpressClasses.vue
- **Route**: `/client/express-classes`
- **Features**:
  - List all client's express classes
  - Filter by status (inquiry, scope_review, priced, assigned, in_progress, completed)
  - Search by course, discipline, or ID
  - Stats cards (Total, Inquiry, In Progress, Completed)
  - Click to view details
  - Pagination support

### 4. ClientExpressClassDetail.vue
- **Route**: `/client/express-classes/:id`
- **Status**: ⏳ **TODO** - Need to create this view
- **Planned Features**:
  - Overview tab (class info, course details, dates, pricing)
  - Writer information
  - Messages tab
  - Files tab
  - Installment schedule (if applicable)

---

## ⏳ **PENDING: Writer Views**

### 1. WriterSpecialOrders.vue
- **Route**: `/writer/special-orders`
- **Status**: ⏳ **TODO**
- **Planned Features**:
  - List all assigned special orders
  - Filter by status
  - Search functionality
  - Stats cards
  - Quick actions (view, start work, submit)

### 2. WriterExpressClasses.vue
- **Route**: `/writer/express-classes`
- **Status**: ⏳ **TODO**
- **Planned Features**:
  - List all assigned express classes
  - Filter by status
  - Search functionality
  - Stats cards
  - School login details (if assigned)
  - Quick actions

### 3. Writer Dashboard Integration
- **Status**: ⏳ **TODO**
- **Planned Features**:
  - Add summary cards for special orders and express classes
  - Show recent assignments
  - Quick links to view all

---

## 📋 **Routes Added**

```javascript
// Client routes
{
  path: 'client/special-orders',
  name: 'ClientSpecialOrders',
  component: () => import('@/client/views/ClientSpecialOrders.vue'),
  meta: { requiresAuth: true, title: 'My Special Orders', roles: ['client'] },
},
{
  path: 'client/special-orders/:id',
  name: 'ClientSpecialOrderDetail',
  component: () => import('@/client/views/ClientSpecialOrderDetail.vue'),
  meta: { requiresAuth: true, title: 'Special Order Details', roles: ['client'] },
},
{
  path: 'client/express-classes',
  name: 'ClientExpressClasses',
  component: () => import('@/client/views/ClientExpressClasses.vue'),
  meta: { requiresAuth: true, title: 'My Express Classes', roles: ['client'] },
},
{
  path: 'client/express-classes/:id',
  name: 'ClientExpressClassDetail',
  component: () => import('@/client/views/ClientExpressClassDetail.vue'),
  meta: { requiresAuth: true, title: 'Express Class Details', roles: ['client'] },
},
```

---

## 🔗 **Navigation Updates Needed**

### Client Sidebar
- Add "Special Orders" link (after "Orders")
- Add "Express Classes" link (after "Special Orders")

### Writer Sidebar
- Add "Special Orders" link
- Add "Express Classes" link

### Client Dashboard
- Add summary cards for special orders and express classes
- Add quick links

### Writer Dashboard
- Add summary cards for assigned special orders and express classes
- Add quick links

---

## 📝 **Next Steps**

1. ✅ Create ClientSpecialOrders.vue - **DONE**
2. ✅ Create ClientSpecialOrderDetail.vue - **DONE**
3. ✅ Create ClientExpressClasses.vue - **DONE**
4. ⏳ Create ClientExpressClassDetail.vue
5. ⏳ Create WriterSpecialOrders.vue
6. ⏳ Create WriterExpressClassDetail.vue (if needed)
7. ⏳ Create WriterExpressClasses.vue
8. ⏳ Create WriterExpressClassDetail.vue (if needed)
9. ⏳ Update client sidebar navigation
10. ⏳ Update writer sidebar navigation
11. ⏳ Update client dashboard
12. ⏳ Update writer dashboard

---

**Last Updated**: January 9, 2025
