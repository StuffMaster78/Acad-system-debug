# 📢 Announcements Center Design

Design document for the Announcements/News Center feature that integrates Broadcast and Mass Email systems.

## 🎯 Overview

Create a centralized "Announcements Center" (or "News & Updates") section accessible from the dashboard sidebar where:
- **Admins/Superadmins** can create and manage announcements via Broadcast system
- **Admins/Superadmins** can access Mass Email system for marketing campaigns
- **All users** can view announcements, see read status, and acknowledge important ones
- **Admins** can track engagement (who read what, when)
- **Important announcements** can be pinned

## 🏗️ Architecture

### Frontend Structure

```
/announcements (or /news)
├── /announcements (Public view - all users)
│   ├── List view (timeline/feed)
│   ├── Detail view (full announcement)
│   └── Filters (pinned, unread, by date)
│
└── /admin/announcements (Admin management)
    ├── Create/Edit announcements
    ├── View engagement analytics
    ├── Manage pinned announcements
    └── Link to Mass Email system
```

### Backend Structure

```
backend/announcements/
├── models.py (Announcement model - extends BroadcastNotification)
├── views.py (Public + Admin views)
├── serializers.py
├── services/
│   ├── engagement_tracking.py (Track reads, views)
│   └── analytics.py (Engagement metrics)
└── urls.py
```

## 📊 Data Model Extensions

### Announcement Model (extends BroadcastNotification)

```python
class Announcement(BroadcastNotification):
    """
    Extends BroadcastNotification with announcement-specific features.
    """
    # Inherits from BroadcastNotification:
    # - title, message, event_type
    # - website, target_roles, channels
    # - is_active, pinned, expires_at
    # - created_by, created_at
    
    # Additional fields:
    category = models.CharField(
        max_length=50,
        choices=[
            ('news', 'News'),
            ('update', 'System Update'),
            ('maintenance', 'Maintenance'),
            ('promotion', 'Promotion'),
            ('general', 'General'),
        ],
        default='general'
    )
    
    featured_image = models.ImageField(upload_to='announcements/', null=True, blank=True)
    read_more_url = models.URLField(null=True, blank=True)
    
    # Engagement tracking
    view_count = models.IntegerField(default=0)
    unique_viewers = models.ManyToManyField(
        User,
        through='AnnouncementView',
        related_name='viewed_announcements'
    )
    
    class Meta:
        ordering = ['-pinned', '-created_at']
```

### AnnouncementView Model (Track individual views)

```python
class AnnouncementView(models.Model):
    """
    Tracks when a user views an announcement.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    time_spent = models.IntegerField(null=True, blank=True)  # seconds
    acknowledged = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'announcement')
        indexes = [
            models.Index(fields=['announcement', 'viewed_at']),
            models.Index(fields=['user', 'viewed_at']),
        ]
```

## 🎨 UI/UX Design

### Sidebar Navigation Item

```javascript
// Add to DashboardLayout.vue navigationItems
{
    name: 'Announcements',
    to: '/announcements',
    label: 'Announcements',
    icon: '📢',
    roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
    badge: computed(() => unreadAnnouncementsCount.value) // Show unread count
}
```

### Public Announcements View (All Users)

**Features:**
- Timeline/feed layout
- Pinned announcements at top
- Unread indicator badges
- Filter by category, date, read/unread
- Search functionality
- "Mark as read" on view
- Acknowledge button for important announcements

**Layout:**
```
┌─────────────────────────────────────────┐
│  📢 Announcements & News                │
├─────────────────────────────────────────┤
│  [Filter] [Search] [Sort]               │
├─────────────────────────────────────────┤
│  📌 PINNED                               │
│  ┌───────────────────────────────────┐  │
│  │ 🚨 System Maintenance - Jan 15    │  │
│  │ [Unread] [Acknowledge]            │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  📅 RECENT                               │
│  ┌───────────────────────────────────┐  │
│  │ 🎉 New Year Promotion              │  │
│  │ Posted: Jan 1, 2026                │  │
│  │ [Read] [View Details]              │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ 📢 New Features Available         │  │
│  │ Posted: Dec 30, 2025              │  │
│  │ [Read] [View Details]             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Admin Management View

**Features:**
- Create/Edit announcements
- View engagement analytics
- Pin/Unpin announcements
- Track read status per user
- Link to Mass Email system
- Schedule announcements

**Layout:**
```
┌─────────────────────────────────────────┐
│  📢 Manage Announcements                │
├─────────────────────────────────────────┤
│  [+ Create Announcement] [Mass Emails]  │
├─────────────────────────────────────────┤
│  Tabs: [All] [Draft] [Active] [Expired] │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │ System Maintenance                │  │
│  │ 📌 Pinned | Active                │  │
│  │ Views: 1,234 | Read: 890 (72%)    │  │
│  │ [Edit] [Analytics] [Unpin]         │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 🔌 API Endpoints

### Public Endpoints (All Users)

```python
# List announcements (filtered by user's role)
GET /api/v1/announcements/
Query params:
  - category: Filter by category
  - pinned: true/false
  - unread: true/false
  - page, page_size

# Get single announcement
GET /api/v1/announcements/{id}/

# Mark as read (track view)
POST /api/v1/announcements/{id}/view/

# Acknowledge announcement
POST /api/v1/announcements/{id}/acknowledge/

# Get unread count
GET /api/v1/announcements/unread-count/
```

### Admin Endpoints

```python
# Create announcement
POST /api/v1/admin/announcements/
Body: {
    "title": "...",
    "message": "...",
    "category": "news",
    "target_roles": ["client"],
    "channels": ["in_app", "email"],
    "pinned": true,
    "expires_at": "2026-01-15T00:00:00Z"
}

# Update announcement
PATCH /api/v1/admin/announcements/{id}/

# Delete announcement
DELETE /api/v1/admin/announcements/{id}/

# Get engagement analytics
GET /api/v1/admin/announcements/{id}/analytics/
Response: {
    "total_views": 1234,
    "unique_viewers": 890,
    "acknowledged": 750,
    "engagement_rate": 60.8,
    "views_by_role": {...},
    "views_over_time": [...]
}

# Pin/Unpin
POST /api/v1/admin/announcements/{id}/pin/
POST /api/v1/admin/announcements/{id}/unpin/

# Get user read status
GET /api/v1/admin/announcements/{id}/readers/
Response: {
    "readers": [
        {"user": "...", "viewed_at": "...", "acknowledged": true}
    ],
    "non_readers": [...]
}
```

## 🔄 Integration with Existing Systems

### Broadcast System Integration

```python
# When creating announcement, also create broadcast
from notifications_system.services.broadcast_services import BroadcastNotificationService

announcement = Announcement.objects.create(...)

# Create corresponding broadcast
broadcast = BroadcastNotificationService.send_broadcast(
    event="announcement.created",
    title=announcement.title,
    message=announcement.message,
    website=announcement.website,
    channels=announcement.channels,
    target_roles=announcement.target_roles
)

announcement.broadcast = broadcast
announcement.save()
```

### Mass Email System Link

```javascript
// In admin announcements view, add button/link
<router-link to="/admin/email-management">
  <button>📧 Manage Mass Emails</button>
</router-link>

// Or embed mass email creation in announcements
<button @click="createMassEmailFromAnnouncement">
  Send as Mass Email Campaign
</button>
```

## 📈 Engagement Tracking

### View Tracking

```python
# When user views announcement
@action(detail=True, methods=['post'])
def view(self, request, pk=None):
    announcement = self.get_object()
    view, created = AnnouncementView.objects.get_or_create(
        user=request.user,
        announcement=announcement,
        defaults={'viewed_at': timezone.now()}
    )
    
    if created:
        announcement.view_count += 1
        announcement.save(update_fields=['view_count'])
    
    return Response({"viewed": True})
```

### Analytics Service

```python
class AnnouncementAnalyticsService:
    @staticmethod
    def get_engagement_stats(announcement):
        total_users = User.objects.filter(
            role__in=announcement.target_roles
        ).count()
        
        views = AnnouncementView.objects.filter(
            announcement=announcement
        )
        
        return {
            "total_views": views.count(),
            "unique_viewers": views.values('user').distinct().count(),
            "acknowledged": views.filter(acknowledged=True).count(),
            "engagement_rate": (views.count() / total_users * 100) if total_users > 0 else 0,
            "views_by_role": views.values('user__role').annotate(count=Count('id')),
            "views_over_time": views.extra(
                select={'date': 'date(viewed_at)'}
            ).values('date').annotate(count=Count('id'))
        }
```

## 🎯 User Experience Flow

### For Regular Users

1. **See Announcements in Sidebar**
   - Badge shows unread count
   - Click to view announcements

2. **View Announcements Feed**
   - Pinned announcements at top
   - Chronological list below
   - Unread indicators

3. **Read Announcement**
   - Click to view full content
   - Automatically marked as read
   - View tracked

4. **Acknowledge Important Announcements**
   - Click "Acknowledge" button
   - Required for critical announcements
   - Tracked for admin analytics

### For Admins

1. **Access Management Panel**
   - Create new announcements
   - Edit existing announcements
   - View analytics

2. **Create Announcement**
   - Form with title, message, category
   - Select target roles
   - Choose channels (in-app, email, both)
   - Option to pin
   - Set expiration date

3. **Track Engagement**
   - See who read what
   - View engagement rates
   - Export analytics

4. **Link to Mass Email**
   - Convert announcement to mass email
   - Or access mass email system directly

## ✅ Benefits

1. **Centralized Communication**
   - Single source of truth for announcements
   - Reduces email clutter

2. **Better Engagement**
   - Users can browse at their convenience
   - No need to search through emails

3. **Admin Insights**
   - Track who's reading what
   - Measure engagement
   - Optimize communication strategy

4. **User Experience**
   - Familiar news feed pattern
   - Easy to discover important updates
   - Clear read/unread status

5. **Integration**
   - Works with existing broadcast system
   - Links to mass email for marketing
   - Leverages existing notification infrastructure

## 🚀 Implementation Steps

### Phase 1: Basic Announcements View
1. Create Announcement model (extends BroadcastNotification)
2. Create public API endpoints
3. Build frontend announcements list view
4. Add sidebar navigation item

### Phase 2: Engagement Tracking
1. Create AnnouncementView model
2. Implement view tracking
3. Add analytics endpoints
4. Build admin analytics dashboard

### Phase 3: Admin Management
1. Create admin API endpoints
2. Build admin management UI
3. Add create/edit forms
4. Implement pin/unpin functionality

### Phase 4: Integration
1. Link with broadcast system
2. Add mass email integration
3. Add notification badges
4. Implement search and filters

## 📝 Naming Suggestions

- **"Announcements"** - Clear, professional
- **"News & Updates"** - Friendly, approachable
- **"Updates"** - Simple, concise
- **"News Center"** - Modern, engaging
- **"What's New"** - Casual, friendly

**Recommendation**: "Announcements" for professional clarity, or "News & Updates" for a friendlier tone.

## 🔐 Permissions

- **View Announcements**: All authenticated users
- **Create/Edit**: Admin, Superadmin
- **View Analytics**: Admin, Superadmin
- **Pin/Unpin**: Admin, Superadmin
- **Delete**: Admin, Superadmin

## 📊 Analytics Dashboard

Admin view showing:
- Total announcements
- Most viewed announcements
- Engagement rates by role
- Read vs unread statistics
- Time-based engagement trends
- User-level read status

---

**Status**: Design Document  
**Next Steps**: Review and approval, then implementation

