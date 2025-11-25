# Payment Batching System - Payment Structure Table

## Overview
This document shows how payments are structured in the bi-weekly and monthly payment batching system.

---

## Payment Hierarchy Structure

```
PaymentSchedule (Batch)
├── schedule_type: "Bi-Weekly" | "Monthly" | "Manual"
├── scheduled_date: Date when payments should be processed
├── website: Website instance
├── completed: Boolean (true when all payments processed)
└── payments[]: ScheduledWriterPayment[]
    ├── writer_wallet: WriterWallet
    ├── amount: Total payment amount
    ├── status: "Pending" | "Paid"
    └── orders[]: PaymentOrderRecord[]
        ├── order: Order instance
        └── amount_paid: Amount from this order
```

---

## Payment Batch Table Structure

### **Bi-Weekly Payment Batches**

| Batch Reference | Scheduled Date | Writers Count | Total Orders | Total Amount | Status | Actions |
|----------------|----------------|--------------|--------------|--------------|--------|---------|
| BW-20250115 | Jan 15, 2025 | 12 | 45 | $12,450.00 | Pending | View Breakdown, Mark All as Paid |
| BW-20250101 | Jan 1, 2025 | 15 | 52 | $15,230.00 | Completed | View Breakdown |
| BW-20241218 | Dec 18, 2024 | 10 | 38 | $9,850.00 | Completed | View Breakdown |

**Clicking "View Breakdown" shows:**

| Writer Name | Email | Registration ID | Total Amount | Orders Count | Tips | Fines | Status | Payment ID |
|-------------|-------|-----------------|--------------|--------------|------|-------|--------|------------|
| John Doe | john@example.com | Writer #12345 | $1,250.00 | 5 | $50.00 | $0.00 | Pending | PAY-123456 |
| Jane Smith | jane@example.com | Writer #12346 | $980.00 | 3 | $25.00 | $10.00 | Pending | PAY-123457 |
| Bob Johnson | bob@example.com | Writer #12347 | $1,450.00 | 6 | $100.00 | $0.00 | Paid | PAY-123458 |

**Clicking on a Writer's row expands to show:**

| Order ID | Order Topic | Amount Paid | Completed Date |
|----------|-------------|-------------|----------------|
| #1234 | Research Paper on AI | $250.00 | Jan 10, 2025 |
| #1235 | Essay on Climate Change | $200.00 | Jan 12, 2025 |
| #1236 | Case Study Analysis | $300.00 | Jan 13, 2025 |
| #1237 | Literature Review | $280.00 | Jan 14, 2025 |
| #1238 | Thesis Proposal | $220.00 | Jan 15, 2025 |

---

### **Monthly Payment Batches**

| Batch Reference | Scheduled Date | Writers Count | Total Orders | Total Amount | Status | Actions |
|----------------|----------------|--------------|--------------|--------------|--------------|---------|
| MO-20250201 | Feb 1, 2025 | 25 | 120 | $45,680.00 | Pending | View Breakdown, Mark All as Paid |
| MO-20250101 | Jan 1, 2025 | 22 | 98 | $38,950.00 | Completed | View Breakdown |
| MO-20241201 | Dec 1, 2024 | 20 | 85 | $32,450.00 | Completed | View Breakdown |

**Clicking "View Breakdown" shows the same writer-level breakdown as bi-weekly batches.**

---

## Detailed Payment Breakdown Example

### **Batch: BW-20250115 (Bi-Weekly, Jan 15, 2025)**

**Summary:**
- **Total Writers:** 12
- **Total Amount:** $12,450.00
- **Total Orders:** 45
- **Total Tips:** $450.00
- **Total Fines:** $25.00
- **Status:** Pending

**Writers Breakdown:**

| # | Writer | Email | Orders | Base Earnings | Tips | Fines | Total | Status |
|---|--------|-------|--------|---------------|------|-------|-------|--------|
| 1 | John Doe | john@example.com | 5 | $1,200.00 | $50.00 | $0.00 | $1,250.00 | Pending |
| 2 | Jane Smith | jane@example.com | 3 | $965.00 | $25.00 | $10.00 | $980.00 | Pending |
| 3 | Bob Johnson | bob@example.com | 6 | $1,350.00 | $100.00 | $0.00 | $1,450.00 | Paid |
| 4 | Alice Brown | alice@example.com | 4 | $850.00 | $30.00 | $0.00 | $880.00 | Pending |
| 5 | Charlie Wilson | charlie@example.com | 7 | $1,550.00 | $75.00 | $5.00 | $1,620.00 | Pending |
| 6 | Diana Martinez | diana@example.com | 3 | $720.00 | $20.00 | $0.00 | $740.00 | Pending |
| 7 | Edward Lee | edward@example.com | 4 | $980.00 | $40.00 | $0.00 | $1,020.00 | Pending |
| 8 | Fiona Chen | fiona@example.com | 5 | $1,100.00 | $50.00 | $0.00 | $1,150.00 | Pending |
| 9 | George Taylor | george@example.com | 2 | $450.00 | $15.00 | $0.00 | $465.00 | Pending |
| 10 | Hannah White | hannah@example.com | 4 | $920.00 | $35.00 | $10.00 | $945.00 | Pending |
| 11 | Ian Davis | ian@example.com | 3 | $680.00 | $20.00 | $0.00 | $700.00 | Pending |
| 12 | Julia Anderson | julia@example.com | 3 | $750.00 | $0.00 | $0.00 | $750.00 | Pending |

**Expanded View for John Doe (Writer #1):**

| Order ID | Topic | Service Type | Pages | Amount | Completed Date |
|----------|-------|--------------|-------|--------|----------------|
| #1234 | Research Paper on AI | Essay | 10 | $250.00 | Jan 10, 2025 |
| #1235 | Essay on Climate Change | Essay | 8 | $200.00 | Jan 12, 2025 |
| #1236 | Case Study Analysis | Case Study | 12 | $300.00 | Jan 13, 2025 |
| #1237 | Literature Review | Literature Review | 11 | $280.00 | Jan 14, 2025 |
| #1238 | Thesis Proposal | Thesis | 9 | $220.00 | Jan 15, 2025 |

**Tips for John Doe:**
- Order #1234: $20.00 (Jan 10, 2025)
- Order #1236: $30.00 (Jan 13, 2025)

**Fines for John Doe:**
- None

**Total for John Doe:**
- Base Earnings: $1,200.00
- Tips: $50.00
- Fines: $0.00
- **Net Total: $1,250.00**

---

## Payment Request Structure

### **Payment Requests Table (Writers Tab)**

| Writer Name | Email | Requested Amount | Available Balance | Reason | Status | Requested Date | Actions |
|-------------|-------|------------------|-------------------|--------|--------|---------------|---------|
| John Doe | john@example.com | $500.00 | $1,250.00 | Need funds for emergency | Pending | Jan 16, 2025 | Approve / Reject |
| Jane Smith | jane@example.com | $300.00 | $980.00 | - | Approved | Jan 15, 2025 | View Details |
| Bob Johnson | bob@example.com | $200.00 | $1,450.00 | - | Rejected | Jan 14, 2025 | View Notes |

---

## Payment Status Flow

```
Pending → [Admin Approves] → Approved → [Processed] → Paid
         ↓
      [Admin Rejects] → Rejected
```

---

## Payment Schedule Preferences

### **Writer Payment Schedule Settings**

| Writer | Payment Schedule | Payment Date Preference | Manual Requests Enabled |
|--------|------------------|------------------------|-------------------------|
| John Doe | Bi-Weekly | 1, 15 | Yes |
| Jane Smith | Monthly | 1 | No |
| Bob Johnson | Bi-Weekly | 5, 20 | Yes |
| Alice Brown | Monthly | 15 | No |

**Payment Date Calculation:**
- **Bi-Weekly with "1, 15":** Payments on 1st and 15th of each month
- **Bi-Weekly with "5, 20":** Payments on 5th and 20th of each month
- **Monthly with "1":** Payment on 1st of each month
- **Monthly with "15":** Payment on 15th of each month

---

## Summary Statistics Dashboard

### **Payment Overview Cards**

| Metric | Bi-Weekly | Monthly | Total |
|--------|-----------|--------|-------|
| **Total Amount** | $25,680.00 | $45,680.00 | $71,360.00 |
| **Total Payments** | 24 | 25 | 49 |
| **Pending Amount** | $12,450.00 | $45,680.00 | $58,130.00 |
| **Paid Amount** | $13,230.00 | $0.00 | $13,230.00 |
| **Total Writers** | 12 | 25 | 37 |
| **Total Orders** | 45 | 120 | 165 |

---

## Payment Processing Workflow

1. **Batch Generation:**
   - System generates batches based on writer payment schedule preferences
   - Calculates payment dates using `payment_date_preference`
   - Includes only completed/approved earnings
   - Excludes already-paid orders

2. **Batch Review:**
   - Admin views batch breakdown
   - Sees all writers and their line items
   - Reviews tips, fines, and adjustments

3. **Payment Processing:**
   - Admin clicks "Mark All as Paid" or "Clear Payments" (same action)
   - All payments in batch are marked as "Paid"
   - Batch status changes to "Completed"
   - Writer wallets are updated

4. **Manual Payment Requests:**
   - Writer requests payment (if enabled)
   - Admin reviews and approves/rejects
   - If approved, creates manual payment schedule
   - Payment is processed in next batch or immediately

---

## Key Features

✅ **Bi-Weekly Payments:** Every 2 weeks based on writer preference  
✅ **Monthly Payments:** Once per month based on writer preference  
✅ **Detailed Breakdowns:** See all writers and line items in each batch  
✅ **Payment Requests:** Writers can request manual payments (if enabled)  
✅ **No Duplicates:** System ensures orders aren't paid twice  
✅ **Only Completed Earnings:** Only includes completed/approved orders  
✅ **Clear = Mark as Paid:** "Clear Payments" marks all as paid (same as "Mark All as Paid")  

---

## Notes

- **Clear Payments** and **Mark All as Paid** are the same action - both mark payments as paid
- Payment dates are calculated based on writer's `payment_date_preference`
- Only completed/approved orders are included in batches
- System prevents duplicate payments across time windows
- Tips and fines are calculated per payment period
- Manual payment requests create "Manual" type payment schedules

