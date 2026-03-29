# Editor Management Workflow

## Overview

The editor management system allows editors to review and edit orders that writers have submitted. The workflow supports three assignment methods:
1. **Auto-Assignment**: System automatically assigns orders to available editors
2. **Manual Assignment**: Admin/Superadmin manually assigns orders to specific editors
3. **Self-Claiming**: Editors can claim unassigned orders themselves

---

## Workflow

### 1. Order Submission → Editor Assignment

```
Writer submits order (status: in_progress → submitted)
    ↓
Order moves to 'under_editing' status
    ↓
EditorAssignmentService.auto_assign_order() attempts auto-assignment
    ↓
[If editor available] → Task assigned to editor (status: pending)
[If no editor available] → Task marked as 'unclaimed'
```

**Auto-Assignment Logic:**
- Finds active editors who haven't reached max concurrent tasks
- Prioritizes editors with matching expertise (subject, paper type)
- Balances workload by assigning to editors with fewer active tasks

---

## Editor Task Assignment

### Assignment Types

- **`auto`**: System automatically assigned
- **`manual`**: Admin/superadmin manually assigned
- **`claimed`**: Editor self-claimed the task

### Task Status Flow

```
pending → in_review → completed
   ↓
unclaimed (if no editor available)
   ↓
rejected (if editor rejects task)
```

---

## Editor Actions

### 1. Claim Order (Self-Assignment)

**Endpoint**: `POST /api/v1/editor-management/tasks/claim/`

**Request:**
```json
{
  "order_id": 123
}
```

**Behavior:**
- Editor claims an unassigned or unclaimed order
- Requires: `can_self_assign = True` and editor hasn't reached max concurrent tasks
- Creates/updates `EditorTaskAssignment` with `assignment_type='claimed'`

---

### 2. Start Review

**Endpoint**: `POST /api/v1/editor-management/tasks/{task_id}/start_review/`

**Behavior:**
- Editor starts working on the task
- Changes status: `pending` → `in_review`
- Records `started_at` timestamp

---

### 3. Submit Review

**Endpoint**: `POST /api/v1/editor-management/tasks/submit_review/`

**Request:**
```json
{
  "task_id": 456,
  "quality_score": 8.5,
  "issues_found": "Minor grammar issues found",
  "corrections_made": "Fixed spelling errors, improved clarity",
  "recommendations": "Overall good work",
  "is_approved": true,
  "requires_revision": false,
  "revision_notes": "",
  "edited_files": [123, 124]
}
```

**Behavior:**
- Creates `EditorReviewSubmission` record
- If `is_approved = true` and `requires_revision = false`:
  - Task status → `completed`
  - Order status → `reviewed`
  - Client notified
- If `requires_revision = true`:
  - Task remains `in_review`
  - Order status → `revision_requested`
  - Writer notified with revision notes

---

### 4. Complete Task

**Endpoint**: `POST /api/v1/editor-management/tasks/complete_task/`

**Request:**
```json
{
  "task_id": 456,
  "final_notes": "Final review completed"
}
```

**Behavior:**
- Marks task as `completed`
- Updates editor's `orders_reviewed` count
- Records completion time

---

### 5. Reject Task

**Endpoint**: `POST /api/v1/editor-management/tasks/reject_task/`

**Request:**
```json
{
  "task_id": 456,
  "reason": "Order quality too poor, needs admin review"
}
```

**Behavior:**
- Marks task as `rejected`
- Notifies admin/superadmin
- Task becomes available for reassignment

---

### 6. Unclaim Task

**Endpoint**: `POST /api/v1/editor-management/tasks/unclaim/`

**Request:**
```json
{
  "task_id": 456
}
```

**Behavior:**
- Editor releases the task
- Task becomes `unclaimed` (available for others)
- Task can be claimed again by another editor

---

## Admin Actions

### Manual Assignment

**Endpoint**: `POST /api/v1/editor-management/admin-assignments/assign/`

**Request:**
```json
{
  "order_id": 123,
  "editor_id": 45,
  "notes": "Assign to this editor due to expertise"
}
```

**Behavior:**
- Admin manually assigns order to specific editor
- Overrides auto-assignment if task already exists
- Notifies the assigned editor

---

## Available Tasks Queue

**Endpoint**: `GET /api/v1/editor-management/tasks/available_tasks/`

**Response:**
- Lists all unassigned/unclaimed tasks for editor's website
- Shows tasks in `under_editing` status
- Editors can claim any available task

---

## Editor Dashboard

**Endpoint**: `GET /api/v1/editor-management/profiles/dashboard_stats/`

**Response:**
```json
{
  "active_tasks_count": 3,
  "pending_tasks_count": 2,
  "in_review_tasks_count": 1,
  "available_tasks_count": 5,
  "recent_completions": 12,
  "can_take_more_tasks": true,
  "max_concurrent_tasks": 5,
  "total_orders_reviewed": 150
}
```

---

## Editor Profile Settings

### EditorProfile Fields

- `can_self_assign`: Whether editor can claim tasks (default: `True`)
- `max_concurrent_tasks`: Maximum tasks editor can work on (default: 5)
- `expertise_subjects`: M2M relationship to `order_configs.Subject`
- `expertise_paper_types`: M2M relationship to `order_configs.PaperType`

### Auto-Assignment Priority

1. **Matching Expertise**: Editors with expertise in order's subject/paper type
2. **Workload Balance**: Editors with fewer active tasks
3. **Availability**: Active editors who haven't reached max concurrent tasks

---

## Review Submission Details

### EditorReviewSubmission Model

Tracks detailed review information:
- `quality_score`: 0.00-10.00 quality rating
- `issues_found`: Problems identified during review
- `corrections_made`: What editor fixed/changed
- `recommendations`: Suggestions for writer/client
- `is_approved`: Whether work approved for delivery
- `requires_revision`: Whether revision needed from writer
- `revision_notes`: Notes for writer if revision needed
- `edited_files`: List of file IDs that were edited

---

## Notifications

Editors receive notifications for:
- **Task Assigned**: When task is auto-assigned or manually assigned
- **Task Claimed**: When another editor claims a task you were assigned
- **Reminders**: For pending tasks (if implemented)
- **Urgent**: For tasks approaching deadline

---

## Performance Tracking

### EditorPerformance Model

Tracks:
- `average_review_time`: Average time to complete reviews
- `total_orders_reviewed`: Total completed reviews
- `late_reviews`: Reviews completed past deadline
- `average_quality_score`: Average admin rating
- `revisions_requested_count`: How many revisions editor requested
- `approvals_count`: How many orders approved for delivery

---

## API Endpoints Summary

### Editor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/editor-management/profiles/` | List editor profiles |
| GET | `/api/v1/editor-management/profiles/{id}/` | Get editor profile |
| GET | `/api/v1/editor-management/profiles/dashboard_stats/` | Dashboard stats |
| GET | `/api/v1/editor-management/tasks/` | List assigned tasks |
| GET | `/api/v1/editor-management/tasks/available_tasks/` | Available tasks to claim |
| POST | `/api/v1/editor-management/tasks/claim/` | Claim an order |
| POST | `/api/v1/editor-management/tasks/{id}/start_review/` | Start reviewing |
| POST | `/api/v1/editor-management/tasks/submit_review/` | Submit review |
| POST | `/api/v1/editor-management/tasks/complete_task/` | Complete task |
| POST | `/api/v1/editor-management/tasks/reject_task/` | Reject task |
| POST | `/api/v1/editor-management/tasks/unclaim/` | Unclaim task |
| GET | `/api/v1/editor-management/reviews/` | List review submissions |
| GET | `/api/v1/editor-management/notifications/` | List notifications |
| POST | `/api/v1/editor-management/notifications/mark_all_read/` | Mark all read |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/editor-management/admin-assignments/assign/` | Manually assign order |

---

## Integration Points

### Automatic Integration

1. **Order Submission**: When writer submits order, `MoveOrderToEditingService` automatically attempts editor assignment
2. **Order Status**: Order status transitions based on review submission:
   - `under_editing` → `reviewed` (if approved)
   - `under_editing` → `revision_requested` (if revision needed)

### Manual Integration

- Admins can manually assign orders via admin panel or API
- Editors can claim available orders from their dashboard
- Support can escalate orders to specific editors

---

## Best Practices

### For Editors

1. **Claim Responsibly**: Only claim tasks you can complete
2. **Start Review Promptly**: Start reviewing when you begin work
3. **Submit Detailed Reviews**: Provide quality feedback
4. **Unclaim if Needed**: If you can't complete, unclaim so others can take it

### For Admins

1. **Monitor Workload**: Check editor dashboard stats regularly
2. **Balance Assignments**: Distribute tasks fairly
3. **Set Expertise**: Configure editor expertise areas for better auto-assignment
4. **Adjust Limits**: Modify `max_concurrent_tasks` based on editor capacity

---

## Future Enhancements

1. **Performance Metrics Calculation Service**: Automatic calculation of editor performance metrics
2. **Task Prioritization**: Priority queue based on deadline, order value, etc.
3. **Workload Balancing**: Advanced algorithms for optimal task distribution
4. **Collaborative Editing**: Multiple editors working on same order
5. **Editor Ratings**: Client/writer ratings of editor work
6. **Skill Matching**: Advanced matching based on historical performance

