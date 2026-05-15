# Celery Tasks

## Task schedule overview

| Task | Schedule | File |
|---|---|---|
| `process_auto_offline` | Every 5 minutes | `availability_tasks.py` |
| `cleanup_expired_windows` | Hourly | `availability_tasks.py` |
| `run_weekly_aggregation` | Sunday 23:00 UTC | `performance_tasks.py` |
| `run_level_progression` | Monday 04:00 UTC | `performance_tasks.py` |
| `backfill_writer_metrics` | Manual trigger | `performance_tasks.py` |
| `evaluate_weekly_rewards` | Monday 06:00 UTC | `reward_tasks.py` |
| `evaluate_monthly_rewards` | 1st of month 07:00 UTC | `reward_tasks.py` |
| `evaluate_lifetime_rewards` | Monday 08:00 UTC | `reward_tasks.py` |

## Ordering dependency

Monday tasks must run in order:

```
Sunday  23:00  run_weekly_aggregation
               └─ snapshots + composite scores written

Monday  04:00  run_level_progression
               └─ reads snapshots written Sunday
               └─ MUST run after aggregation is complete

Monday  06:00  evaluate_weekly_rewards
               └─ reads metrics from Sunday aggregation
               └─ MUST run after level progression

Monday  08:00  evaluate_lifetime_rewards
               └─ reads all-time performance
               └─ can run any time after aggregation
```

Do not schedule any Monday task before `run_weekly_aggregation` finishes.
The 5-hour gap (23:00 → 04:00) is the safety margin for the aggregation
run across all writers. Adjust if writer count grows significantly.

## Availability tasks

### `process_auto_offline`
Runs every 5 minutes. Finds writers with
`auto_go_offline=True` and `last_seen_at` older than
`auto_offline_after_minutes`. Marks `WriterStatus.status = OFFLINE`.

### `cleanup_expired_windows`
Runs hourly. Finds `WriterAvailabilityWindow` records where
`end_at < now` and `is_active=True`. Marks them inactive and
calls `AvailabilityService.end_window()` for each.

## Performance tasks

### `run_weekly_aggregation`
Iterates all active writers on all websites.
For each writer: `WriterMetricsSnapshotService.create_or_update()`.
Two-pass:
1. Create/update all snapshots and compute composite scores.
2. Compute percentile ranks in bulk across all writers per website.

Runs in chunks of 50 writers to manage memory.

### `run_level_progression`
Iterates all active writers. For each:
`LevelProgressionService.evaluate_writer()`.
Checks N consecutive snapshots for promotion.
Checks most recent snapshot for demotion.
One level change maximum per evaluation cycle.

### `backfill_writer_metrics`
Manual admin trigger. Accepts `website_id` and optional
`writer_registration_id` to target a single writer.
Used after data corrections or writer imports.

## Reward tasks

### `evaluate_weekly_rewards`
Runs `RewardEvaluationService.evaluate_all(period="weekly")`.
Checks `WriterRewardCriteria` with `evaluation_period=weekly`.
Evaluates all active writers against each active criteria.

### `evaluate_monthly_rewards`
First of every month 07:00 UTC.
Runs `RewardEvaluationService.evaluate_all(period="monthly")`.

### `evaluate_lifetime_rewards`
Weekly, Monday 08:00 UTC.
Runs `RewardEvaluationService.evaluate_all(period="lifetime")`.
Lifetime rewards are granted once — the service deduplicates
via a `UniqueConstraint` on `(writer, criteria)`.

## Celery beat configuration

```python
# settings/celery.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Availability
    "process-auto-offline": {
        "task": "writer_management.tasks.availability_tasks.process_auto_offline",
        "schedule": 300,  # every 5 minutes
    },
    "cleanup-expired-windows": {
        "task": "writer_management.tasks.availability_tasks.cleanup_expired_windows",
        "schedule": 3600,  # hourly
    },
    # Performance
    "weekly-aggregation": {
        "task": "writer_management.tasks.performance_tasks.run_weekly_aggregation",
        "schedule": crontab(hour=23, minute=0, day_of_week=0),  # Sunday
    },
    "level-progression": {
        "task": "writer_management.tasks.performance_tasks.run_level_progression",
        "schedule": crontab(hour=4, minute=0, day_of_week=1),  # Monday
    },
    # Rewards
    "evaluate-weekly-rewards": {
        "task": "writer_management.tasks.reward_tasks.evaluate_weekly_rewards",
        "schedule": crontab(hour=6, minute=0, day_of_week=1),  # Monday
    },
    "evaluate-monthly-rewards": {
        "task": "writer_management.tasks.reward_tasks.evaluate_monthly_rewards",
        "schedule": crontab(hour=7, minute=0, day_of_month=1),  # 1st
    },
    "evaluate-lifetime-rewards": {
        "task": "writer_management.tasks.reward_tasks.evaluate_lifetime_rewards",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Monday
    },
}
```

## Error handling

All tasks log failures per writer and continue to the next.
A single writer's aggregation failure does not abort the batch.
Failed writers are logged at `ERROR` level with `registration_id`
so they can be reprocessed via `backfill_writer_metrics`.
