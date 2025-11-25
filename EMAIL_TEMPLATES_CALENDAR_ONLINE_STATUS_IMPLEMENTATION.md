# Email Templates, Calendar, and Online Status Implementation Plan

**Date:** November 24, 2025  
**Status:** Implementation in Progress

---

## 📧 Email Templates System

### Current State
✅ **Backend Models Exist:**
- `EmailTemplate` model in `mass_emails/models.py` - for campaign templates
- `NotificationTemplate` model in `notifications_system/models/notifications_template.py` - for notification templates
- Email rendering utilities exist

✅ **Backend API Exists:**
- `EmailTemplateViewSet` in `mass_emails/views.py` - CRUD for templates
- Endpoint: `/api/v1/mass-emails/email-templates/`

### What's Needed
1. **Frontend Admin UI** for managing email templates
2. **Template Preview** functionality
3. **Template Variables** documentation
4. **Default Templates** seeding

---

## 📅 Calendar Feature

### Current State
✅ **Backend Endpoint Exists:**
- `/api/v1/writer-management/dashboard/calendar/` in `writer_management/views_dashboard.py`
- Returns calendar data with order deadlines

✅ **Frontend Component Exists:**
- `frontend/src/views/writers/WriterCalendar.vue` - Full calendar UI
- Route configured: `/writer/calendar`

### What's Needed
1. **Test the endpoint** - verify it returns correct data
2. **Fix any integration issues** - ensure frontend calls backend correctly
3. **Add client calendar** - clients should see their order deadlines too

---

## 👥 Online Status Visibility

### Current State
✅ **Backend Functionality:**
- `get_user_online_status` endpoint in `users/views.py` - returns online status + timezone + day/night
- Privacy-aware serializers in `users/serializers/privacy.py` - includes `is_online` and `is_daytime`

✅ **Frontend Component:**
- `OnlineStatusIndicator.vue` - displays online status and day/night indicator
- Supports `showTimeIndicator` prop for day/night display

### What's Needed
1. **Add OnlineStatusIndicator to relevant views:**
   - Order detail pages (show writer/client status)
   - User lists (show online status)
   - Chat/messaging interfaces
   - Writer dashboard (show assigned clients)
   - Client dashboard (show assigned writers)

2. **Ensure proper permissions:**
   - Clients can see writer online status
   - Writers can see client online status (with day/night indicator)
   - Staff (admin/superadmin/support) can see all with day/night for clients

3. **Verify day/night calculation:**
   - Currently uses 6 AM - 8 PM as daytime
   - Should work correctly for all timezones

---

## 🎯 Implementation Tasks

### Task 1: Email Templates Admin UI
- [ ] Create frontend component for template management
- [ ] Add route for template management
- [ ] Add template preview functionality
- [ ] Document template variables

### Task 2: Calendar Feature Testing & Fixes
- [ ] Test calendar endpoint
- [ ] Fix any integration issues
- [ ] Add client calendar view

### Task 3: Online Status Integration
- [ ] Add OnlineStatusIndicator to OrderDetail.vue
- [ ] Add to user lists/chat interfaces
- [ ] Add to writer/client dashboards
- [ ] Verify permissions work correctly

---

## 📝 Next Steps

1. Test calendar endpoint
2. Add OnlineStatusIndicator to key views
3. Create email template management UI
4. Test all features end-to-end

