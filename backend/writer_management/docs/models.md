# Models Reference

## Identity & Level

### `WriterProfile`
The writer domain anchor. One per writer per website.

| Field | Type | Description |
|---|---|---|
| `account_profile` | OneToOne → AccountProfile | Platform identity link |
| `registration_id` | CharField | Stable ID: `WR-YYYYMMDD-RANDOM6` |
| `public_uuid` | UUIDField | Opaque API identifier. Never expose PK |
| `pen_name` | CharField | Display name. Changed via `WriterPenNameChangeRequest` |
| `timezone` | CharField | IANA timezone string |
| `bio` | TextField | Professional bio shown to clients (≤ 500 chars) |
| `qualifications` | JSONField | List of `{title, institution, year, verified}` |
| `years_of_experience` | PositiveSmallIntegerField | Self-declared |
| `writer_level` | FK → WriterLevel | Current tier. Null = unassigned |
| `is_verified` | BooleanField | Admin-controlled |
| `verification_status` | CharField | `unverified / pending / verified / rejected` |
| `onboarding_status` | CharField | Writer-domain onboarding state |
| `joined_at` | DateTimeField | Profile creation timestamp |
| `is_deleted` | BooleanField | Soft delete flag |
| `deleted_at` | DateTimeField | Soft delete timestamp |

**Mutation**: `WriterProfileService` only. Never write directly.

---

### `WriterLevel`
Dynamic, admin-defined tier. One per website.

**Mutation**: Admin via Django admin or level management API.

---

### `WriterLevelSettings`
Pay rates and capacity defaults for a level. OneToOne with `WriterLevel`.

**Key fields**: `base_pay_per_page`, `max_active_orders`, `tip_percentage`,
`urgent_multiplier`.

---

### `WriterLevelCriteria`
Promotion and demotion thresholds. OneToOne with `WriterLevel`.

**Key methods**: `meets_promotion_thresholds(snapshot)`,
`breaches_demotion_thresholds(snapshot)`.

---

### `WriterLevelChangeLog`
Append-only audit of every level change. Never updated.

---

## Runtime State

### `WriterStatus`
Real-time presence. One per writer. High churn.

| Field | Description |
|---|---|
| `status` | `online / offline / away / busy` |
| `last_seen_at` | Updated on every heartbeat |
| `status_message` | Optional short message |

**Mutation**: `mark_online()`, `mark_offline()`, `record_heartbeat()` methods only.
Has NO effect on assignment routing.

---

### `WriterCapacity`
Workload state. One per writer. High churn.

| Field | Description |
|---|---|
| `can_take_orders` | Platform discipline gate. Set by `DisciplineService` |
| `is_accepting_orders` | Writer's own instant toggle |
| `active_orders_count` | Cached count. Updated via `F()` expressions only |
| `override_max_active_orders` | Per-writer admin override. Null = use level default |

**Mutation**: `assignment_service` (counters), `availability_service` (toggle),
`discipline_service` (can_take_orders).

---

### `WriterDisciplineState`
Cached discipline summary. One per writer.
Rebuilt by `WriterStatusService.recompute()` after every discipline event.

| Field | Description |
|---|---|
| `is_suspended` | True when active `WriterSuspension` exists |
| `is_blacklisted` | True when active `WriterBlacklist` exists |
| `is_on_probation` | True when active `WriterProbation` exists |
| `active_warning_count` | Non-expired, non-voided warnings |
| `active_strike_count` | Non-voided strikes |
| `lifetime_strike_count` | All strikes ever |

**Never write directly.** Read-only except via `WriterStatusService`.

---

### `WriterAvailabilityWindow`
Declared unavailability period. Zero or more per writer.
Active window blocks assignment routing.

---

### `WriterAvailabilityPreference`
Standing availability preferences. One per writer.

---

## Discipline Source Records

### `WriterWarning`
Temporary formal notice. Expires. Can be voided.

| Field | Description |
|---|---|
| `category` | `late_delivery / communication / quality / ...` |
| `expires_at` | When it stops counting. Null = permanent |
| `is_voided` | Admin error correction. Preserves audit trail |

**Active** = `is_active=True AND is_voided=False AND (expires_at > now OR null)`

---

### `WriterStrike`
Permanent record. Never expires. Can be voided.

| Field | Description |
|---|---|
| `category` | `plagiarism / off_platform / academic_misconduct / ...` |
| `evidence_notes` | Internal only. Not shown to writer |
| `is_voided` | Error correction only. Record preserved |

**Counts toward threshold** = `is_voided=False`

---

### `WriterSuspension`, `WriterBlacklist`, `WriterProbation`
One active record per writer at a time (partial UniqueConstraint).
Blacklist supersedes suspension — cannot be both simultaneously.

---

### `WriterPenalty`
Financial penalty record. Actual deduction executed by `writer_compensation`.
This model is the disciplinary record only.

---

### `WriterDisciplineConfig`
Site-level thresholds. One per website.

---

## Configuration

### `WriterConfig`
Site-level assignment workflow settings.

| Field | Description |
|---|---|
| `takes_enabled` | Writers can self-assign vs must request |
| `auto_assign_enabled` | System auto-routes orders |
| `max_takes_per_writer` | Fallback ceiling (overridden by level then writer) |

---

### `WriterWarningEscalationConfig`
Warning count thresholds.

| Field | Description |
|---|---|
| `admin_alert_threshold` | Notify admins at this count |
| `auto_probation_threshold` | Auto-probate at this count. 0 = disabled |
| `auto_suspension_threshold` | Auto-suspend at this count. 0 = disabled |
| `default_warning_duration_days` | Default expiry. Overridable per warning |

---

## Performance

### `WriterPerformance`
Lifetime running totals. One per writer. Updated via `F()` expressions.
**Never set directly.**

### `WriterPerformanceSnapshot`
Frozen period record. Append-only. Used for level progression.
Rate fields stored as **proportions** (0.0000–1.0000).

### `WriterPerformanceMetrics`
Weekly aggregation with ranking. Rate fields stored as **percentages** (0–100).

---

## Recognition

### `WriterReward` / `WriterRewardCriteria`
Criteria define thresholds per evaluation period (weekly/monthly/lifetime).
Rewards are the grant records. Financial disbursement via `writer_compensation`.

---

## Application

### `WriterApplication`
Pre-onboarding record. Exists before `WriterProfile`.

**States**: `pending → under_review → approved / rejected / withdrawn`

One active application per email per website (partial UniqueConstraint).

---

## Logs

| Model | Purpose |
|---|---|
| `WriterActionLog` | Discipline events audit trail |
| `WriterActivityLog` | Writer platform actions |
| `WriterActivityTracking` | Last seen / login presence cache |
| `WriterIPLog` | IP addresses for fraud detection |
| `WriterProfileUpdateLog` | Profile field change audit |
| `WriterFileDownloadLog` | Resource file access via files_management app |

---

## Notes & Resources

| Model | Purpose |
|---|---|
| `WriterNote` | Internal admin notes. Never shown to writers |
| `WriterPenNameChangeRequest` | Admin-approved pen name changes |
| `WriterResource` / `WriterResourceCategory` | Admin-managed development resources |
| `WriterResourceView` | Resource view tracking |