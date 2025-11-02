# Editor Management Enhancements

## Overview

This document describes the enhancements added to the editor management system, including performance metrics calculation and comprehensive dashboard functionality.

---

## Performance Metrics Calculation

### EditorPerformanceCalculationService

A comprehensive service for calculating and updating editor performance metrics.

#### Features

1. **Automatic Performance Calculation**
   - Calculates average review time
   - Tracks total orders reviewed
   - Counts late reviews (completed after deadline)
   - Calculates average quality score from admin ratings
   - Tracks revisions requested count
   - Tracks approvals count

2. **Performance Statistics**
   - Get detailed stats over a time period (default 30 days)
   - Calculate approval rates
   - Calculate revision rates
   - Track average completion times
   - Monitor on-time completion rates

3. **Editor Rankings**
   - Rank editors by performance
   - Consider multiple factors (total reviews, quality score, late reviews)
   - Configurable limit (top N editors)

---

## Dashboard Service

### EditorDashboardService

Comprehensive dashboard data generation for editors and admins.

#### Editor Dashboard Features

1. **Summary Statistics**
   - Active tasks count
   - Pending/in-review tasks breakdown
   - Available tasks to claim
   - Recent completions
   - Urgent tasks (due in next 7 days)
   - Overdue tasks
   - Current workload percentage
   - Capacity status

2. **Performance Metrics**
   - Total orders reviewed
   - Average review time (in hours)
   - Late reviews count
   - Average quality score
   - Revisions requested
   - Approvals count
   - Performance stats over time period

3. **Task Details**
   - Breakdown by status (pending, in_review, completed, rejected, unclaimed)
   - Breakdown by assignment type (auto, manual, claimed)
   - Active tasks list with deadlines
   - Available tasks queue
   - Urgent tasks with days until deadline
   - Overdue tasks with days overdue

4. **Recent Activity**
   - Last 10 actions logged
   - Action types and timestamps
   - Related order information

5. **Recent Reviews**
   - Last 10 review submissions
   - Quality scores
   - Approval/revision status
   - Submission timestamps

#### Admin Team Overview Features

1. **Team Statistics**
   - Total editors count
   - Active editors (with current tasks)
   - Unassigned tasks count
   - Total active tasks across team

2. **Individual Editor Stats**
   - Active tasks per editor
   - Max capacity vs utilization
   - Utilization percentage
   - Total reviews completed
   - Average quality score
   - Can take more tasks status

3. **Top Performers**
   - Ranked list of best performing editors
   - Based on reviews, quality scores, and performance

---

## API Endpoints

### Editor Endpoints

#### Enhanced Dashboard
**GET** `/api/v1/editor-management/profiles/dashboard_stats/?days=30`

Returns comprehensive dashboard data including:
- Summary statistics
- Performance metrics
- Task breakdowns
- Recent activity
- Recent reviews

**Query Parameters:**
- `days` (optional): Number of days for statistics (default: 30)

**Response Example:**
```json
{
  "summary": {
    "active_tasks_count": 3,
    "pending_tasks_count": 2,
    "in_review_tasks_count": 1,
    "available_tasks_count": 5,
    "recent_completions": 12,
    "urgent_tasks_count": 1,
    "overdue_tasks_count": 0,
    "can_take_more_tasks": true,
    "max_concurrent_tasks": 5,
    "current_workload_percent": 60.0
  },
  "performance": {
    "total_orders_reviewed": 150,
    "average_review_time_hours": 2.5,
    "late_reviews": 3,
    "average_quality_score": 8.5,
    "approval_rate_percent": 85.0,
    "revision_rate_percent": 15.0
  },
  "tasks": {
    "breakdown_by_status": {...},
    "breakdown_by_assignment_type": {...},
    "active_tasks": [...],
    "available_tasks": [...],
    "urgent_tasks": [...],
    "overdue_tasks": [...]
  },
  "recent_activity": [...],
  "recent_reviews": [...]
}
```

#### Enhanced Performance
**GET** `/api/v1/editor-management/performance/`

Returns performance metrics (auto-calculated on access).

**GET** `/api/v1/editor-management/performance/detailed-stats/?days=30`

Returns detailed performance statistics over a time period.

**Response Example:**
```json
{
  "period_days": 30,
  "total_tasks_assigned": 25,
  "completed_tasks": 22,
  "active_tasks": 3,
  "average_completion_time_hours": 2.3,
  "approval_rate_percent": 85.0,
  "revision_rate_percent": 15.0,
  "average_quality_score": 8.5,
  "admin_ratings_average": 9.0,
  "total_admin_ratings": 18
}
```

### Admin Endpoints

#### Team Overview
**GET** `/api/v1/editor-management/admin-assignments/team_overview/`

Returns overview of all editors in the website/tenant.

**Response Example:**
```json
{
  "total_editors": 10,
  "active_editors": 8,
  "unassigned_tasks": 5,
  "total_active_tasks": 25,
  "editor_stats": [
    {
      "editor_id": 1,
      "editor_name": "John Doe",
      "active_tasks": 3,
      "max_tasks": 5,
      "utilization_percent": 60.0,
      "total_reviewed": 150,
      "average_quality_score": 8.5,
      "can_take_more": true
    }
  ],
  "top_performers": [...]
}
```

#### Editor Rankings
**GET** `/api/v1/editor-management/admin-assignments/rankings/?limit=10`

Returns ranked list of top performing editors.

**Query Parameters:**
- `limit` (optional): Number of editors to return (default: 10)

**Response Example:**
```json
[
  {
    "rank": 1,
    "editor_id": 5,
    "editor_name": "Jane Smith",
    "total_reviews": 200,
    "average_quality_score": 9.2,
    "late_reviews": 2,
    "approval_rate": 90.0
  }
]
```

#### Recalculate Performance
**POST** `/api/v1/editor-management/admin-assignments/recalculate_performance/`

Triggers performance recalculation.

**Request Body:**
```json
{
  "editor_id": 5  // Optional: recalculate specific editor, or omit for all
}
```

**Response:**
```json
{
  "calculated": 10,
  "failed": 0,
  "total": 10
}
```

---

## Performance Metrics Details

### Calculated Metrics

1. **Average Review Time**
   - Calculated from `started_at` to `reviewed_at` for completed tasks
   - Stored as `DurationField` in `EditorPerformance`

2. **Total Orders Reviewed**
   - Synced with `EditorProfile.orders_reviewed`
   - Updated automatically when task is completed

3. **Late Reviews**
   - Count of reviews completed after order deadline
   - Helps identify time management issues

4. **Average Quality Score**
   - From admin ratings on `EditorTaskAssignment.editor_rating`
   - Optional rating system (1-5 scale)

5. **Revisions Requested Count**
   - Total number of reviews where `requires_revision = True`
   - Indicates quality standards

6. **Approvals Count**
   - Total number of reviews where `is_approved = True`
   - Indicates positive work quality

### Performance Statistics (Time-based)

1. **Approval Rate**
   - Percentage of reviews that were approved
   - Formula: `(approved_count / total_reviews) * 100`

2. **Revision Rate**
   - Percentage of reviews requiring revision
   - Formula: `(revision_count / total_reviews) * 100`

3. **Average Completion Time**
   - Average time to complete tasks over period
   - In hours for readability

4. **Admin Ratings Average**
   - Average of admin ratings for editor
   - Only includes tasks with ratings

---

## Dashboard Features

### Editor Dashboard

**Purpose**: Give editors a comprehensive view of their work and performance.

**Key Sections:**
1. **At-a-Glance Summary**: Quick stats about current workload
2. **Performance Metrics**: Overall performance indicators
3. **Task Management**: Detailed breakdown of tasks
4. **Recent Activity**: Recent actions and reviews
5. **Urgent Items**: Tasks requiring immediate attention

### Admin Team Overview

**Purpose**: Help admins manage editor team effectively.

**Key Sections:**
1. **Team Statistics**: Overall team status
2. **Individual Editor Stats**: Per-editor utilization and performance
3. **Top Performers**: Ranked list for recognition
4. **Unassigned Tasks**: Tasks waiting for assignment

---

## Integration

### Automatic Calculation

- Performance metrics are calculated automatically when accessed
- Can be triggered manually via admin endpoint
- Recommended: Run periodic recalculation (e.g., daily via Celery)

### Dashboard Data

- Dashboard data is generated on-demand
- No caching currently (can be added for performance)
- All queries are optimized with `select_related` and `prefetch_related`

---

## Best Practices

### For Editors

1. **Monitor Dashboard Regularly**: Check urgent and overdue tasks
2. **Review Performance Stats**: Identify areas for improvement
3. **Maintain Workload Balance**: Don't exceed capacity
4. **Track Approval Rates**: Higher approval rate = better quality

### For Admins

1. **Monitor Team Overview**: Ensure workload is balanced
2. **Review Rankings**: Identify top performers and those needing support
3. **Recalculate Performance**: Run periodic recalculation for accuracy
4. **Use Utilization Data**: Ensure editors are working efficiently

---

## Future Enhancements

1. **Caching**: Cache dashboard data for better performance
2. **Real-time Updates**: WebSocket updates for dashboard
3. **Performance Goals**: Set and track performance goals per editor
4. **Trend Analysis**: Show performance trends over time
5. **Predictive Analytics**: Predict task completion times
6. **Automated Alerts**: Notify editors of urgent/overdue tasks
7. **Skill Development**: Track skill improvement over time
8. **Workload Forecasting**: Predict future workload based on patterns

