# Feature/Messages-Fixes Branch - Issues to Address

This document tracks all issues to be addressed on the `feature/messages-fixes` branch.

## Status: In Progress

### High Priority (User-facing bugs)

1. ✅ **Editor typing backwards** - FIXED: Removed RTL direction from RichTextEditor toolbar
2. ⏳ **Writer dashboard message threads** - Threads created under wrong tabs (client vs writer)
3. ⏳ **Request order button** - Should disable/turn to "Requested Already" after clicking
4. ⏳ **Writer dashboard requests visibility** - Writers can't see their requests on orders, dialog box bug

### Medium Priority (UX improvements)

5. ⏳ **Messaging lag** - Fine-tune lag when selecting recipient
6. ⏳ **Support ticket creation** - Add file uploads, allow completing orders
7. ⏳ **Submit button flow** - Open order details, check for final file, add pre-submission checklist

### Lower Priority (Features)

8. ⏳ **Revision instructions section** - Add section for clients/support/admin to paste/write revision instructions
9. ⏳ **File categories** - Universal categories (Final Draft, First Draft, etc. for writers; materials, sample, etc. for clients)
10. ⏳ **Draft deadline** - Client should indicate deadline, writer should see it
11. ⏳ **Order caching** - Cache orders so users can access them when server is down
12. ⏳ **File management UX** - Make it easier for writers to upload and clients to access files

---

## Implementation Notes

### Issue #1: Editor Typing Backwards ✅
- **Status**: Fixed
- **Change**: Removed `[{ 'direction': 'rtl' }]` from RichTextEditor toolbar
- **File**: `frontend/src/components/common/RichTextEditor.vue`

### Issue #2: Writer Dashboard Message Threads
- **Problem**: When writer sends messages to support, threads are created under client tabs and vice versa
- **Root Cause**: Backend thread role assignment logic in `ThreadService.create_thread`
- **Fix**: Review and fix `recipient_role` assignment in `backend/communications/services/thread_service.py`

### Issue #3: Request Order Button
- **Problem**: Button doesn't disable/turn to "Requested Already" after clicking
- **Files to check**: 
  - `frontend/src/views/orders/OrderDetail.vue`
  - `frontend/src/views/writers/OrderQueue.vue`
  - `frontend/src/views/dashboard/components/WriterDashboard.vue`

### Issue #4: Writer Dashboard Requests Visibility
- **Problem**: Writers can't see their requests on orders, dialog box bug
- **Files to check**: `frontend/src/views/dashboard/components/WriterDashboard.vue`

### Issue #5: Messaging Lag
- **Problem**: Lag when selecting recipient to type a message
- **Files to check**: 
  - `frontend/src/components/messages/NewMessageModal.vue`
  - `frontend/src/components/order/OrderNewMessageModal.vue`

### Issue #6: Support Ticket Creation
- **Needs**: 
  - File uploads (backend already supports, need frontend UI)
  - Allow completing orders from tickets
- **Files**: `frontend/src/views/support/Tickets.vue`

### Issue #7: Submit Button Flow
- **Needs**: 
  - Open order details page
  - Check for final file
  - Add pre-submission checklist
- **Files**: `frontend/src/views/orders/OrderDetail.vue`

### Issue #8: Revision Instructions Section
- **Needs**: Section where clients/support/admin can paste/write revision instructions
- **Files**: `frontend/src/views/orders/OrderDetail.vue`

### Issue #9: File Categories
- **Needs**: Universal categories for different file types
- **Backend**: Already has `OrderFileCategory` model
- **Frontend**: Need to enhance UI in `frontend/src/views/orders/OrderDetail.vue`

### Issue #10: Draft Deadline
- **Needs**: Client should indicate deadline, writer should see it
- **Backend**: `DraftRequest` model exists but may need deadline field
- **Files**: `backend/orders/models.py`, `frontend/src/views/orders/OrderDetail.vue`

### Issue #11: Order Caching
- **Needs**: Cache orders in localStorage/IndexedDB for offline access
- **Approach**: Create a caching service/utility

### Issue #12: File Management UX
- **Needs**: Easier uploads for writers, better access for clients, mark final files clearly
- **Files**: `frontend/src/views/orders/OrderDetail.vue`

