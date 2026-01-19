# Admin Workflows Documentation

**Last Updated**: January 9, 2025

This document provides comprehensive guides for admin workflows, focusing on the newly implemented features for Special Orders and Express Classes management.

---

## Table of Contents

1. [Special Orders Management](#special-orders-management)
2. [Express Classes Management](#express-classes-management)
3. [Fines Management](#fines-management)

---

## Special Orders Management

### Overview

Special Orders are custom orders that don't fit the standard pricing structure. They can be either:
- **Predefined**: Uses a predefined pricing structure
- **Estimated**: Requires price negotiation with the client

### Key Features

#### 1. Price Negotiation (Estimated Orders)

**When to Use**: For estimated special orders that need pricing discussion with clients.

**Steps**:
1. Navigate to Special Order detail page
2. In the "Financial Information" section, click "Negotiate Price" or "Set Price"
3. Enter either:
   - **Total Cost**: The full amount for the order
   - **Price Per Day**: Automatically calculates total based on duration
4. Add optional negotiation notes (visible to client)
5. Click "Set Price" or "Update Price"
6. Client is automatically notified of the new price

**Notes**:
- Deposit is automatically calculated (typically 50% of total)
- Can be called multiple times for negotiation
- Only available for orders in "inquiry" or "awaiting_approval" status

#### 2. Follow-up Tracking

**Purpose**: Record important actions and notes for order management.

**Steps**:
1. In the "Follow-up Tracking" section, click "Add Follow-up"
2. Select follow-up type:
   - Client Contact
   - Price Negotiation
   - Writer Assignment
   - Payment Follow-up
   - Progress Check
   - Quality Review
   - Other
3. Enter notes describing what was done or discussed
4. Optionally add "Next Action" (e.g., "Follow up in 2 days")
5. Click "Save Follow-up"

**Benefits**:
- Maintains a clear history of interactions
- Helps track pending actions
- Visible to all admins working on the order

#### 3. Writer Assignment

**Steps**:
1. Navigate to order detail page
2. In "Writer Information" section, click "Assign" or "Reassign"
3. Search and select a writer
4. Set payment (amount or percentage)
5. Add optional admin notes
6. Click "Assign Writer"

---

## Express Classes Management

### Overview

Express Classes are single-class requests that require school login access and writer assignment.

### Key Features

#### 1. School Details Management

**Purpose**: Store and manage school portal login credentials for writers.

**Steps**:
1. Navigate to Express Class detail page
2. In "School Details" section, click "Add Details" or "Edit"
3. Enter:
   - **School Login URL**: Portal login page URL
   - **Username**: Login username
   - **Password**: Login password (with show/hide toggle)
   - **Availability Hours**: When writer can access (e.g., "Mon-Fri 9am-5pm EST")
   - **2FA Enabled**: Check if two-factor authentication is required
4. Click "Save Details"

**Security Notes**:
- Passwords are stored securely
- Only admins can view/edit school details
- Writers see login info but not passwords

#### 2. Writer Assignment with Bonus

**Steps**:
1. Ensure class is priced (status must be "priced")
2. In "Writer Information" section, click "Assign Writer"
3. Search and select a writer
4. Set **Bonus Amount** (defaults to class price)
   - This amount is paid as a bonus to the writer
   - Automatically creates a WriterBonus record
5. Add optional admin notes
6. Click "Assign Writer"

**What Happens**:
- Writer is assigned to the class
- WriterBonus is automatically created
- Class status changes to "assigned"
- Writer can access school login details

#### 3. Scope Review & Pricing

**Steps**:
1. For classes in "inquiry" status, click "Review Scope"
2. Set the price for the class
3. Add scope review notes
4. Optionally add admin notes
5. Click "Review Scope & Set Price"

**Result**:
- Class status changes to "priced"
- Client is notified of the price
- Writer assignment becomes available

---

## Fines Management

### Overview

The Fines Management system allows admins to issue fines, review disputes, and manage fine appeals.

### Key Features

#### 1. Approve Dispute

**When to Use**: When a writer's appeal is valid and the fine should be waived.

**Steps**:
1. Navigate to Fines Management → Dispute Queue tab
2. Find the disputed fine
3. Click "Approve" button
4. Enter optional review notes
5. Click "Approve Appeal"

**Result**:
- Fine is automatically waived
- Writer is notified
- Fine status changes to "waived"
- Compensation is restored if applicable

#### 2. Reject Dispute

**When to Use**: When a writer's appeal is not valid and the fine should be upheld.

**Steps**:
1. Navigate to Fines Management → Dispute Queue tab
2. Find the disputed fine
3. Click "Reject" button
4. Enter **required** review notes explaining the rejection
5. Click "Reject Appeal"

**Result**:
- Fine is upheld
- Writer is notified with rejection reason
- Fine status changes to "resolved"

#### 3. View Fine Details

**Steps**:
1. In any fines list, click "View" on a fine
2. Modal displays:
   - Fine ID and order link
   - Amount and status
   - Fine type and reason
   - Issued date
   - Appeal information (if applicable)
3. Actions available:
   - **Waive Fine**: Manually waive the fine
   - **Void Fine**: Void the fine (if status is "issued")

---

## Best Practices

### Special Orders

1. **Price Negotiation**:
   - Always add negotiation notes explaining the price
   - Consider client budget when setting prices
   - Use multiple rounds of negotiation if needed

2. **Follow-ups**:
   - Record follow-ups immediately after actions
   - Be specific in notes
   - Set clear next actions

3. **Writer Assignment**:
   - Assign writers promptly after pricing is set
   - Set appropriate payment amounts
   - Document any special requirements in admin notes

### Express Classes

1. **School Details**:
   - Verify login credentials before saving
   - Update availability hours if they change
   - Mark 2FA status accurately

2. **Writer Assignment**:
   - Ensure class is fully priced before assignment
   - Set bonus amount based on class complexity
   - Verify writer has access to school portal

### Fines Management

1. **Dispute Review**:
   - Review all evidence before making a decision
   - Provide clear, professional review notes
   - Be consistent in approval/rejection criteria

2. **Fine Details**:
   - Always review full fine details before taking action
   - Check appeal status if applicable
   - Document all actions taken

---

## Troubleshooting

### Special Orders

**Issue**: "Negotiate Price" button not visible
- **Solution**: Check order status - must be "inquiry" or "awaiting_approval"
- **Solution**: Verify order type is "estimated"

**Issue**: Follow-ups not showing
- **Solution**: Follow-ups are parsed from admin_notes - ensure format is correct
- **Solution**: Check that follow-ups were saved successfully

### Express Classes

**Issue**: Cannot assign writer
- **Solution**: Ensure class status is "priced"
- **Solution**: Verify class has a price set

**Issue**: School details not saving
- **Solution**: Check all required fields are filled
- **Solution**: Verify URL format is correct

### Fines

**Issue**: Cannot approve/reject dispute
- **Solution**: Verify you have admin/superadmin/support role
- **Solution**: Check appeal status is "pending"
- **Solution**: Ensure review notes are provided (required for rejection)

---

## API Endpoints Reference

### Special Orders
- `POST /api/special-orders/api/special-orders/{id}/set-price/` - Set/negotiate price

### Express Classes
- `POST /api/class-management/express-classes/{id}/assign_writer/` - Assign writer with bonus
- `PATCH /api/class-management/express-classes/{id}/` - Update class (including school details)

### Fines
- `POST /api/fines/fine-appeals/{id}/review/` - Review appeal (approve/reject)

---

**For additional support or questions, contact the development team.**
