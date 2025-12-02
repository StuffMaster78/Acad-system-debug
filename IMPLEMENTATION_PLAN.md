# Implementation Plan: Enhanced Order Management Features

## Overview
This document outlines the implementation plan for multiple features to improve order management, writer engagement, file handling, pricing, and user experience.

## Features to Implement

### 1. Writer Assignment Acknowledgment ✅ (Backend Models Created)
**Status**: Backend models created, need migrations and services

**Components**:
- `WriterAssignmentAcknowledgment` model created
- Tracks: acknowledgment, message sent, files downloaded
- Reminder system for engagement

**Next Steps**:
- Create migration
- Create serializer and ViewSet
- Add acknowledgment endpoint
- Create reminder service
- Frontend: Writer acknowledgment UI

### 2. File Access Logging ✅ (Enhanced)
**Status**: FileDownloadLog exists, enhanced download tracking

**Components**:
- Enhanced `FileDownloadLog` model (already exists)
- Download tracking in file download endpoint
- Writer download tracking for acknowledgment

**Next Steps**:
- Create admin view for download logs
- Frontend: Download log viewer for admins

### 3. File Versioning and Final Paper Marking ✅ (Backend Enhanced)
**Status**: OrderFile model enhanced with versioning

**Components**:
- Added version field to OrderFile
- Added status field (draft, revision, final, archived)
- Added is_final_paper boolean
- Auto-versioning on save
- Final paper marking method

**Next Steps**:
- Create migration
- Update file upload endpoint to handle versioning
- Frontend: File version display and Final Paper marking UI
- Submit button visibility logic

### 4. Message Reminders ✅ (Backend Models Created)
**Status**: Backend models created

**Components**:
- `MessageReminder` model created
- Tracks unread/unresponded messages
- Exponential backoff reminder scheduling

**Next Steps**:
- Create migration
- Create serializer and ViewSet
- Create reminder service (Celery task)
- Frontend: Message reminder UI

### 5. Review Reminders ✅ (Backend Models Created)
**Status**: Backend models created

**Components**:
- `ReviewReminder` model created
- Tracks review and rating status
- Scheduled reminders (1, 3, 7 days)

**Next Steps**:
- Create migration
- Create serializer and ViewSet
- Create reminder service (Celery task)
- Frontend: Review reminder UI

### 6. Pricing Calculator with Persistence ✅ (Backend Models Created)
**Status**: Backend models created

**Components**:
- `PricingCalculatorSession` model created
- Stores pricing calculations for anonymous/logged-in users
- 24-hour expiration
- Conversion tracking

**Next Steps**:
- Create migration (need to check if pricing app exists or use pricing_configs)
- Create API endpoints for calculator
- Frontend: Enhanced pricing calculator with persistence
- Link to order creation after signup

### 7. Badges System Enhancement
**Status**: Need to check existing badges

**Components Needed**:
- Badge models (check if exists)
- Badge assignment logic
- Global badges for clients
- Badge display components

**Next Steps**:
- Review existing badge system
- Enhance badge assignment logic
- Frontend: Badge display and management

## Implementation Priority

### Phase 1 (Critical - Immediate)
1. File versioning and Final Paper marking (migration + endpoints)
2. Writer acknowledgment system (migration + endpoints)
3. File download logging enhancement (already in place)

### Phase 2 (High Priority)
4. Pricing calculator persistence (migration + endpoints)
5. Message reminders (migration + services)
6. Review reminders (migration + services)

### Phase 3 (Enhancement)
7. Badges system enhancement
8. Frontend UI improvements for all features

## Database Migrations Needed

1. `orders/migrations/XXXX_add_writer_acknowledgment.py`
2. `orders/migrations/XXXX_add_message_reminders.py`
3. `orders/migrations/XXXX_add_review_reminders.py`
4. `order_files/migrations/XXXX_enhance_order_file_versioning.py`
5. `pricing_configs/migrations/XXXX_add_calculator_session.py` (or create pricing app)

## API Endpoints Needed

### Writer Acknowledgment
- `POST /api/orders/{id}/acknowledge/` - Writer acknowledges assignment
- `GET /api/orders/{id}/acknowledgment/` - Get acknowledgment status
- `POST /api/orders/{id}/mark-message-sent/` - Mark message sent
- `GET /api/writers/acknowledgments/` - List writer acknowledgments

### File Management
- `POST /api/order-files/{id}/mark-final/` - Mark file as final paper
- `GET /api/order-files/{id}/versions/` - Get file versions
- `GET /api/order-files/download-logs/` - Get download logs (admin)

### Message Reminders
- `GET /api/message-reminders/` - Get user's message reminders
- `POST /api/message-reminders/{id}/mark-read/` - Mark as read
- `POST /api/message-reminders/{id}/mark-responded/` - Mark as responded

### Review Reminders
- `GET /api/review-reminders/` - Get user's review reminders
- `POST /api/review-reminders/{id}/mark-reviewed/` - Mark as reviewed
- `POST /api/review-reminders/{id}/mark-rated/` - Mark as rated

### Pricing Calculator
- `POST /api/pricing/calculate/` - Calculate price
- `POST /api/pricing/save-session/` - Save pricing session
- `GET /api/pricing/session/{session_key}/` - Get saved session
- `POST /api/pricing/convert-to-order/` - Convert session to order

## Frontend Components Needed

1. **Writer Dashboard Enhancements**:
   - Assignment acknowledgment card
   - Engagement checklist (acknowledge, message, download files)
   - Reminder notifications

2. **File Management UI**:
   - File version list
   - Final Paper marking button
   - Version comparison
   - Prominent download button for clients
   - File status indicators

3. **Message Reminders UI**:
   - Unread message badges
   - Reminder notifications
   - Quick response buttons

4. **Review Reminders UI**:
   - Review prompt cards
   - Rating interface
   - Reminder notifications

5. **Pricing Calculator**:
   - Enhanced calculator with real-time pricing
   - Session persistence
   - "Continue to Order" flow after signup

6. **Badges Display**:
   - Badge showcase
   - Badge progress indicators
   - Global badge leaderboard

## Services/Tasks Needed

1. **Reminder Services** (Celery tasks):
   - `send_writer_engagement_reminders` - Daily task
   - `send_message_reminders` - Hourly task
   - `send_review_reminders` - Daily task

2. **Acknowledgment Service**:
   - Auto-create acknowledgment on writer assignment
   - Check engagement status
   - Send reminders

3. **File Versioning Service**:
   - Handle file uploads with versioning
   - Manage Final Paper marking
   - Archive old versions

## Testing Requirements

1. Unit tests for all new models
2. Integration tests for API endpoints
3. Frontend component tests
4. E2E tests for complete flows

## Notes

- All models use proper indexes for performance
- Reminders use exponential backoff to avoid spam
- File versioning prevents data loss
- Pricing sessions expire after 24 hours
- All features respect user permissions and roles

