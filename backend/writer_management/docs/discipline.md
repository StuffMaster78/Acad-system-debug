# Discipline System

## Two mechanisms

| | Warning | Strike |
|---|---|---|
| Nature | Temporary formal notice | Permanent record |
| Expires | Yes — configurable days | Never |
| Voidable | Yes | Yes (error correction only) |
| Threshold | Active count | Lifetime non-voided count |
| Triggers | Probation, suspension | Suspension, blacklist |
| Examples | Late delivery, comms failure | Plagiarism, identity fraud |

## Threshold evaluation

After every new **warning**:

```
active_warnings >= admin_alert_threshold     → notify admins
active_warnings >= auto_probation_threshold  → DisciplineService.place_on_probation()
active_warnings >= auto_suspension_threshold → DisciplineService.suspend()
```

After every new **strike**:

```
lifetime_strikes >= auto_suspend_on_strikes    → DisciplineService.suspend()
lifetime_strikes >= auto_blacklist_on_strikes  → DisciplineService.blacklist()
```

Thresholds configured in `WriterDisciplineConfig` and
`WriterWarningEscalationConfig` per website.

## Severity hierarchy

```
Warning (temporary)
  ↓ escalates to
Probation (flagged but can still work)
  ↓ escalates to
Suspension (cannot take orders, time-limited or indefinite)
  ↓ escalates to
Blacklist (permanent exclusion — supersedes all other states)
```

Blacklist supersedes suspension. A writer cannot be both simultaneously.
`WriterDisciplineState` has a `CheckConstraint` enforcing this.

## State cache

`WriterDisciplineState` is rebuilt after every discipline event by
`WriterStatusService.recompute()`. It reads all source records and
writes the derived state atomically using `select_for_update`.

**Never read source records for routing decisions** — read
`WriterDisciplineState` instead. It is the fast path.

## Void vs delete

Discipline records are **never deleted**. They are voided.

```python
# Correct — void preserves audit trail
WriterWarningService.void_warning(warning, voided_by=admin, reason="...")
DisciplineService.void_strike(strike, voided_by=admin, reason="...")

# Wrong — never do this
warning.delete()
```

Voided records remain in the database with `is_voided=True`.
They are excluded from threshold counts but visible in admin.

## Example escalation scenario

```
Week 1: Warning — late delivery         (active: 1)
Week 1: Warning — communication failure (active: 2)
Week 2: Warning — quality issue         (active: 3 → admin alert)
Week 3: Warning — availability abuse    (active: 4)
Week 3: Warning — policy violation      (active: 5 → auto-probation)
Week 4: Strike  — plagiarism confirmed  (lifetime: 1 → immediate suspension)
Week 6: (suspension lifted)
Week 8: Strike  — off-platform contact  (lifetime: 2)
Week 12: Strike — identity fraud        (lifetime: 3 → auto-blacklist)
```

## Service ownership

| Action | Service |
|---|---|
| Issue / void warning | `WriterWarningService` |
| Issue / void strike | `DisciplineService` |
| Suspend / lift | `DisciplineService` |
| Blacklist / lift | `DisciplineService` |
| Probation / end | `DisciplineService` |
| Apply penalty | `DisciplineService` |
| Rebuild cache | `WriterStatusService.recompute()` |
| Expire timed actions | `DisciplineService.expire_ended_actions()` |
