# API Reference

Base path: `/api/writer-management/`

## Authentication

All endpoints require authentication unless noted.
Permissions: `IsAdminUser`, `IsWriterUser`, `IsAdminOrWriterOwner`.

---

## Profile

### `GET writers/`
List all writers on the site. Admin only.

**Query params**:
- `onboarding_status` — filter by status
- `verification_status` — filter by status
- `is_verified` — `true / false`
- `is_deleted` — `true / false`
- `level` — WriterLevel PK
- `search` — searches `registration_id` and `pen_name`

**Response**: `WriterProfileSummarySerializer[]`

---

### `GET writers/<registration_id>/`
Full writer detail. Admin only.

**Response**: `WriterProfileDetailSerializer`

---

### `GET writers/<public_uuid>/card/`
Public client-facing writer card. Authenticated.

**Response**: `WriterProfilePublicSerializer`

---

### `GET me/profile/`
Writer's own profile. Writer only.

**Response**: `WriterProfileDetailSerializer`

---

### `PATCH me/profile/`
Update own profile. Writer only.

**Body**:
```json
{
  "bio": "string (max 500 chars)",
  "timezone": "Africa/Nairobi",
  "qualifications": [{"title": "...", "institution": "...", "year": 2020}],
  "years_of_experience": 4
}
```

---

### `POST writers/<registration_id>/delete/`
Soft delete. Admin only. Body: `{"reason": "..."}`.

### `POST writers/<registration_id>/restore/`
Restore. Admin only. Body: `{"reason": "..."}`.

---

## Availability

### `GET me/availability/`
```json
{
  "active_window": null | {window object},
  "upcoming_windows": [{window object}]
}
```

### `POST me/availability/declare/`
```json
{
  "start_at": "2025-02-01T00:00:00Z",
  "end_at": "2025-02-07T00:00:00Z",
  "reason": "personal",
  "note": "Holiday"
}
```

### `POST me/availability/<pk>/end/`
End window early. No body.

### `POST me/availability/toggle/`
```json
{"is_accepting_orders": false}
```

### `PATCH me/availability/preferences/`
```json
{
  "preferred_start_hour": 9,
  "preferred_end_hour": 17,
  "preferred_days": [0, 1, 2, 3, 4],
  "auto_go_offline": true,
  "auto_offline_after_minutes": 30
}
```

---

## Discipline

### `GET writers/<rid>/discipline/`
Returns `WriterDisciplineStateSerializer`.

### `GET writers/<rid>/warnings/`
Query params: `category`, `is_active`, `is_voided`, `issued_after`, `issued_before`.

### `POST writers/<rid>/warnings/issue/`
```json
{
  "reason": "Order #4821 delivered 2 hours late. First offence.",
  "category": "late_delivery",
  "expires_days": 30
}
```

### `POST warnings/<pk>/void/`
```json
{"reason": "Issued in error — delivery was on time per system log."}
```

### `POST writers/<rid>/strikes/issue/`
```json
{
  "reason": "Confirmed plagiarism on Order #7823. Turnitin similarity 40%.",
  "category": "plagiarism",
  "evidence_notes": "Turnitin report ID: TT-20250113-8821"
}
```

### `POST strikes/<pk>/void/`
```json
{"reason": "False positive confirmed — similarity to writer's own prior work."}
```

### `POST writers/<rid>/suspend/`
```json
{
  "reason": "Auto-suspended: 7 warnings in 30 days.",
  "duration_days": 7
}
```
Omit `duration_days` for indefinite suspension.

### `POST writers/<rid>/lift-suspension/`
```json
{"reason": "Suspension period served. Writer may resume."}
```

### `POST writers/<rid>/blacklist/`
```json
{"reason": "Identity fraud confirmed. Account sharing investigation complete."}
```

### `POST writers/<rid>/lift-blacklist/`
```json
{"reason": "Investigation concluded. Reinstated by senior admin."}
```

### `POST writers/<rid>/probation/`
```json
{
  "reason": "Quality concerns across 3 consecutive orders.",
  "duration_days": 30
}
```

### `POST writers/<rid>/penalties/`
```json
{
  "reason": "late_submission",
  "amount": "15.00",
  "order_id": 4821,
  "notes": "Client requested refund due to 4-hour late delivery."
}
```

---

## Performance

### `GET writers/<rid>/performance/`
Lifetime totals. Admin or writer owner.

### `GET writers/<rid>/performance/snapshots/`
Paginated period snapshots. Admin only.
Query params: `period_start_after`, `period_end_before`, `is_processed`.

### `GET writers/<rid>/performance/metrics/`
Paginated weekly metrics. Admin only.

---

## Rewards

### `GET writers/<rid>/rewards/`
Reward history. Admin or writer owner.

---

## Notes

### `GET writers/<rid>/notes/`
Admin only. Query param: `include_sensitive=true` (requires elevated role).

### `POST writers/<rid>/notes/create/`
```json
{
  "note": "Consistent quality on economics orders. Consider priority routing.",
  "is_pinned": true,
  "is_sensitive": false,
  "related_order_id": 4821
}
```

### `PATCH notes/<pk>/`
```json
{
  "note": "Updated note text.",
  "is_pinned": false
}
```

### `DELETE notes/<pk>/`
No body. Returns 204.

### `POST notes/<pk>/pin/`
Toggles pin state. No body.

---

## Resources

### `GET resources/`
Active resources. Writer only.
Query param: `category=<pk>`.

### `GET resources/<pk>/`
Resource detail. Records a view automatically.

### `POST resources/<pk>/download/`
Records a download. Returns:
```json
{
  "detail": "Download recorded.",
  "file_url": "https://..."
}
```

---

## Applications

### `GET applications/`
Admin list. Query params: `status`, `search`, `submitted_after`, `submitted_before`.

### `GET applications/<pk>/`
Admin detail view.

### `POST applications/submit/`
Public endpoint.
```json
{
  "full_name": "David Kamau",
  "email": "david.kamau@gmail.com",
  "phone_number": "+254712345678",
  "country": "Kenya",
  "education_level": "Master's degree",
  "years_of_experience": 4,
  "subjects": ["Finance", "Economics"],
  "application_text": "Cover letter text here..."
}
```

### `POST applications/<pk>/review/`
Admin. No body. Marks `UNDER_REVIEW`.

### `POST applications/<pk>/approve/`
```json
{
  "initial_level_id": 3,
  "require_review": true
}
```
Both fields optional. Creates `AccountProfile` + `WriterProfile` atomically.

### `POST applications/<pk>/reject/`
```json
{
  "rejection_reason": "Insufficient sample work quality.",
  "admin_notes": "Internal: did not meet subject expertise threshold."
}
```

### `POST applications/<pk>/withdraw/`
No body. Applicant action.

---

## Error responses

All endpoints return standard DRF error shapes:

```json
{"detail": "Writer not found."}
{"field_name": ["This field is required."]}
```

Validation errors return `HTTP 400`. Permission errors return `HTTP 403`.
Not found returns `HTTP 404`.

