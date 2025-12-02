# Order Actions Summary

This document summarizes all available order actions and how they change based on order status, assignment state, and user role.

## Overview

Order actions are dynamically displayed based on:
- **Order Status**: The current state of the order (available, in_progress, submitted, etc.)
- **Assignment State**: Whether the order is assigned to a writer or available
- **User Role**: Writer, Client, Admin, SuperAdmin, Support, or Editor
- **User Relationship**: Whether the user is the assigned writer, order owner (client), or has admin privileges

---

## Order States

### 1. **Available** (Not Yet Assigned)
Order is in the queue, waiting for a writer to take or request it.

### 2. **Assigned/In Progress** (Assigned to Writer)
Order has been assigned to a writer and work is in progress.

### 3. **Revision States** (Revision Requested/In Progress)
Client or admin has requested changes to the submitted work.

### 4. **Submitted/Completed** (Work Submitted)
Writer has completed and submitted the work for review.

### 5. **Closed/Archived** (Final States)
Order has been completed, closed, or archived.

---

## Actions by Role and State

### 👤 **WRITER Actions**

#### **For Available Orders (Not Assigned)**
- ✅ **Take Order** 
  - **When**: Order status is `available` and not yet assigned
  - **Action**: Immediately assigns order to writer
  - **Requirements**: Writer must have capacity (not at order limit)
  - **Color**: Emerald green

- 📋 **Request Order**
  - **When**: Order status is `available` and not yet assigned
  - **Action**: Submits request for admin approval
  - **Requirements**: Must provide reason (10-2000 characters)
  - **Color**: Violet
  - **Note**: Shows "Requested" if already requested

#### **For Assigned Orders (Writer is Assigned)**
- 🚀 **Start Order**
  - **When**: Order status is `available` or `reassigned` AND writer is assigned
  - **Action**: Transitions order to `in_progress`
  - **Color**: Blue

- 📤 **Submit Order**
  - **When**: Order status is `in_progress`, `draft`, or `revision_in_progress` AND writer is assigned
  - **Action**: Submits completed work for review
  - **Color**: Green

- ✏️ **Start Revision**
  - **When**: Order status is `revision_requested` AND writer is assigned
  - **Action**: Begins working on requested revisions
  - **Color**: Indigo

- ▶️ **Resume Order**
  - **When**: Order status is `on_hold` AND writer is assigned
  - **Action**: Resumes work on a held order
  - **Color**: Teal

- ⏰ **Request Deadline Extension**
  - **When**: Order status is `in_progress`, `assigned`, or `draft` AND writer is assigned
  - **Action**: Opens modal to request deadline extension
  - **Requirements**: Must provide new deadline and reason
  - **Color**: Orange

- 🛑 **Request Hold**
  - **When**: Order status is `in_progress`, `assigned`, or `draft` AND writer is assigned
  - **Action**: Requests to put order on hold
  - **Color**: Yellow

---

### 👥 **CLIENT Actions**

#### **For Active Orders**
- 💳 **Pay Now**
  - **When**: Order is unpaid AND client owns the order
  - **Action**: Opens payment modal
  - **Color**: Primary blue

- ✅ **Mark as Complete**
  - **When**: Order status is `submitted` AND client owns the order
  - **Action**: Marks order as completed
  - **Color**: Blue
  - **Note**: Also available to admins for `submitted` or `in_progress` orders

- 🔄 **Request Revision**
  - **When**: Order status is `completed`, `submitted`, or `approved` AND client owns the order
  - **Action**: Opens modal to request changes
  - **Requirements**: Must provide revision reason
  - **Color**: Orange

- ❌ **Cancel Order**
  - **When**: Order is NOT `completed` or `cancelled` AND client owns the order
  - **Action**: Cancels the order
  - **Color**: Red
  - **Note**: Also available to admins for non-final states

#### **For Completed Orders**
- ⭐ **Submit Review**
  - **When**: Order status is `completed` AND client owns the order
  - **Action**: Opens review submission form
  - **Location**: Review section in Overview tab

- 💰 **Tip Writer**
  - **When**: Order status is `completed`, `submitted`, `approved`, or `closed` AND client owns the order AND order has a writer
  - **Action**: Opens tip modal
  - **Color**: Purple
  - **Note**: Can tip from wallet or credit card

---

### 🔧 **ADMIN/SUPERADMIN/SUPPORT Actions**

- ⚙️ **Order Actions** (Modal)
  - **When**: Admin, SuperAdmin, or Support viewing any order
  - **Action**: Opens comprehensive action modal with all available actions
  - **Includes**: 
    - Assign/Reassign Writer
    - Change Status
    - Move to Editing
    - Approve/Complete
    - Cancel/Reopen
    - Archive/Close
    - And more based on current status
  - **Color**: Purple

- 🔄 **Reopen Order**
  - **When**: Order status is `completed` or `cancelled` AND user is admin
  - **Action**: Reopens a closed/cancelled order
  - **Color**: Yellow

---

## Action Availability Matrix

| Order Status | Writer (Available) | Writer (Assigned) | Client | Admin/Support |
|-------------|-------------------|-------------------|--------|---------------|
| **available** | Take, Request | Start Order | Pay (if unpaid) | All actions |
| **assigned** | - | Start Order, Request Extension, Request Hold | Pay (if unpaid) | All actions |
| **in_progress** | - | Submit Order, Request Extension, Request Hold | Pay (if unpaid) | All actions |
| **on_hold** | - | Resume Order | Pay (if unpaid) | All actions |
| **revision_requested** | - | Start Revision | Request Revision | All actions |
| **revision_in_progress** | - | Submit Order | - | All actions |
| **submitted** | - | - | Complete, Request Revision, Tip | All actions |
| **completed** | - | - | Review, Request Revision, Tip | All actions |
| **approved** | - | - | Request Revision, Tip | All actions |
| **closed** | - | - | Tip | All actions |
| **cancelled** | - | - | - | Reopen, All actions |
| **archived** | - | - | - | All actions |

---

## Special Conditions

### **Writer Capacity Checks**
- **Take Order**: Only available if writer hasn't reached their order limit
- **Request Order**: Always available (no capacity check)

### **Assignment Checks**
- **Assigned Writer Actions**: Only show if `order.writer_id === userId` OR `order.assigned_writer_id === userId`
- **Available Order Actions**: Show for all writers when order is not assigned

### **Payment Requirements**
- **Pay Now**: Only shows if order is unpaid
- **File Downloads**: Final draft files require payment completion

### **Revision States**
- **Request Revision**: Available when order is `completed`, `submitted`, or `approved`
- **Start Revision**: Available when order is `revision_requested` and writer is assigned
- **Submit Revision**: Same as Submit Order when in `revision_in_progress`

---

## Action Flow Examples

### **New Order Flow (Writer)**
1. Order is `available` → Writer sees **Take** or **Request** buttons
2. Writer takes order → Order becomes `assigned` → Writer sees **Start Order**
3. Writer starts → Order becomes `in_progress` → Writer sees **Submit Order**, **Request Extension**, **Request Hold**
4. Writer submits → Order becomes `submitted` → Writer actions disappear

### **Revision Flow**
1. Order is `submitted` or `completed` → Client sees **Request Revision**
2. Client requests revision → Order becomes `revision_requested` → Assigned writer sees **Start Revision**
3. Writer starts revision → Order becomes `revision_in_progress` → Writer sees **Submit Order**
4. Writer submits revision → Order becomes `revised` → Back to review process

### **Hold Flow**
1. Order is `in_progress` → Writer sees **Request Hold**
2. Writer requests hold → Order becomes `on_hold` → Writer sees **Resume Order**
3. Writer resumes → Order becomes `in_progress` → Back to normal flow

---

## Notes

- **Admin/SuperAdmin/Support** have access to a comprehensive action modal that shows all available actions based on current order state
- **Clients** have direct action buttons for common operations (complete, cancel, pay)
- **Writers** have different actions based on whether they're assigned to the order
- All actions include proper validation, error handling, and success feedback
- Actions automatically refresh order data after execution
- Some actions require confirmation dialogs (e.g., Take Order, Cancel Order)

