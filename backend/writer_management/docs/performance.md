# Performance Pipeline

## Three models, three purposes

| Model | Updated | Used for |
|---|---|---|
| `WriterPerformance` | After every order event | Lifetime dashboard, financial mirrors |
| `WriterPerformanceSnapshot` | Weekly/monthly Celery task | Level progression decisions |
| `WriterPerformanceMetrics` | Weekly Celery task | Rankings, rewards, dashboards |

## Weekly pipeline

```
Sunday 23:00 UTC
  run_weekly_aggregation
       │
       └─ For each writer:
            WriterMetricsSnapshotService.create_or_update()
              ├─ Gather order counts (orders app)
              ├─ Gather financials (writer_compensation)
              ├─ Gather ratings (reviews_system)
              ├─ Compute rate proportions
              ├─ Upsert WriterPerformanceSnapshot
              └─ CompositeScoreService.compute_and_save()
                   └─ is_processed = True
            WriterPerformanceMetrics upserted
       │
       └─ _compute_percentile_ranks()
            Bulk update percentile_rank across all writers

Monday 04:00 UTC
  run_level_progression
       │
       └─ For each writer:
            LevelProgressionService.evaluate_writer()
              ├─ _try_promote() — checks N consecutive snapshots
              └─ _try_demote()  — checks most recent snapshot
```

## Composite score weights

| Metric | Weight | Direction |
|---|---|---|
| Average rating (0–5 scaled to 0–1) | 40% | Higher = better |
| Completion rate | 25% | Higher = better |
| Lateness rate | 15% | Lower = better (penalty) |
| Revision rate | 10% | Lower = better (penalty) |
| Dispute rate | 5% | Lower = better (penalty) |
| Cancellation rate | 5% | Lower = better (penalty) |

Score range: 0–100. Computed by `CompositeScoreService.compute()`.

## Rate field conventions

| Model | Convention | Example |
|---|---|---|
| `WriterPerformanceSnapshot` | Proportions 0.0000–1.0000 | `lateness_rate = 0.0500` = 5% |
| `WriterPerformanceMetrics` | Percentages 0–100 | `lateness_rate = 5.00` = 5% |

This distinction matters when writing threshold comparisons.
`WriterLevelCriteria` thresholds are in percentages (matching `WriterPerformanceMetrics`).

## Level progression rules

- One level jump per evaluation cycle.
- Promotion requires N consecutive passing snapshots
  (`WriterLevelCriteria.min_evaluation_periods`).
- Demotion requires only 1 breaching snapshot.
- Level navigation uses `WriterLevel.display_order`
  (lower = higher rank).
- Initial level assigned by `WriterProfileService.assign_initial_level()`.
- Subsequent changes by `LevelProgressionService`.

## Rate card snapshot

When a writer is assigned to an order, `RateCardSnapshotService.capture()`
freezes their current `WriterLevelSettings` values into `RateCardSnapshot`
in `writer_compensation`. This snapshot is the source for all earnings
calculations — `WriterLevelSettings` can be updated freely without
affecting in-progress order earnings.
