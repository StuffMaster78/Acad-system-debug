# Account Deletion Requests - Admin/Superadmin Guide

## 📍 Where to View Deletion Requests

### Backend API Endpoint

**GET** `/api/v1/users/account-deletion/list/`

**Query Parameters:**
- `status` (optional): Filter by status (`pending`, `confirmed`, `rejected`)

**Example:**
```bash
# Get all deletion requests
GET /api/v1/users/account-deletion/list/

# Get only pending requests
GET /api/v1/users/account-deletion/list/?status=pending
```

**Response:**
```json
{
  "count": 5,
  "requests": [
    {
      "id": 1,
      "user_id": 15,
      "user_email": "user@example.com",
      "user_username": "test_user",
      "user_role": "client",
      "user_full_name": "John Doe",
      "reason": "No longer need the service",
      "status": "pending",
      "admin_response": null,
      "request_time": "2024-01-15T10:30:00Z",
      "scheduled_deletion_time": null,
      "confirmation_time": null,
      "rejection_time": null,
      "website": 1
    }
  ]
}
```

### Frontend Location

**Recommended:** Add a tab or section in `/admin/users` (UserManagement.vue)

**Alternative:** Create a dedicated page at `/admin/deletion-requests`

## 🔧 Available Actions

### 1. List All Deletion Requests
- **Endpoint:** `GET /api/v1/users/account-deletion/list/`
- **Permission:** Admin or Superadmin
- **Frontend API:** `usersAPI.getDeletionRequests(status)`

### 2. Approve Deletion Request
- **Endpoint:** `POST /api/v1/users/account-deletion/{id}/approve_deletion/`
- **Permission:** Admin or Superadmin
- **Action:** Freezes the user account and sets status to "confirmed"
- **Frontend API:** `usersAPI.approveDeletionRequest(requestId)`

### 3. Reject Deletion Request
- **Endpoint:** `POST /api/v1/users/account-deletion/{id}/reject_deletion/`
- **Permission:** Admin or Superadmin
- **Body:** `{ "reason": "Optional rejection reason" }`
- **Action:** Rejects the request and unfreezes the account if frozen
- **Frontend API:** `usersAPI.rejectDeletionRequest(requestId, reason)`

### 4. Reinstate Account
- **Endpoint:** `POST /api/v1/users/account-deletion/{id}/reinstate_account/`
- **Permission:** Admin or Superadmin
- **Action:** Unfreezes a frozen account and rejects the deletion request
- **Frontend API:** `usersAPI.reinstateAccount(requestId)`

## 📋 Request Statuses

- **pending**: Request submitted, awaiting admin review
- **confirmed**: Request approved, account frozen, scheduled for deletion
- **rejected**: Request rejected by admin

## 🎨 Frontend Implementation

### Option 1: Add to UserManagement.vue

Add a new tab or section in the UserManagement component:

```vue
<!-- Add tabs -->
<div class="tabs">
  <button @click="activeTab = 'users'">Users</button>
  <button @click="activeTab = 'deletion-requests'">Deletion Requests</button>
</div>

<!-- Deletion Requests Tab -->
<div v-if="activeTab === 'deletion-requests'">
  <!-- List of deletion requests with approve/reject buttons -->
</div>
```

### Option 2: Create Dedicated Component

Create `/src/views/admin/DeletionRequests.vue` and add route:

```javascript
{
  path: 'admin/deletion-requests',
  name: 'DeletionRequests',
  component: () => import('@/views/admin/DeletionRequests.vue'),
  meta: {
    requiresAuth: true,
    title: 'Deletion Requests',
    roles: ['admin', 'superadmin'],
  },
}
```

## ✅ Next Steps

1. **Add UI Component** - Create deletion requests management UI
2. **Add Route** - Add route to router if creating separate page
3. **Test** - Test approve/reject/reinstate functionality

## 📝 Notes

- Only Admin and Superadmin can view and manage deletion requests
- Users with roles: client, writer, support, editor can request deletion
- Admin and Superadmin accounts cannot be deleted
- Superadmin can manage admin accounts through User Management

