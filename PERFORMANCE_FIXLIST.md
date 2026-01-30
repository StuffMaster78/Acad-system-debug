Performance Fix List (Lagging)

Priority 0 (Immediate)
- Add server-side pagination and default ordering on large list endpoints:
  orders, communications, notifications, audit logs, admin lists, tickets, payments.
- Add/verify DB indexes:
  orders(status, website_id, assigned_writer_id, created_at),
  communications(thread_id, created_at),
  notifications(user_id, read_at, created_at),
  tickets(status, created_at),
  payments(order_id, status, created_at).
- Reduce serializer payloads for list views (list vs detail serializers).
- Enable query count logging for slow endpoints (p95) and fix N+1 with select_related/prefetch_related.

Priority 1 (Short-term)
- Cache dashboard summaries for 30-120s (admin, writer, client dashboards).
- Consolidate multi-call dashboards to a single summary endpoint where possible.
- Add ETags/If-Modified-Since to notifications feed + SSE backoff.
- Split heavy Vue pages (OrderDetail, Admin dashboards) into smaller subcomponents to reduce re-render cost.

Priority 2 (Mid-term)
- Background aggregation tables for analytics (orders, payments, performance).
- Async export generation + notifications rather than synchronous responses.
- CDN for static assets, media thumbnails, and public pages.

Frontend quick wins
- Debounce search filters and use virtualized lists for large tables.
- Use route-level code splitting for admin modules (already large).
- Avoid deep watchers on huge objects; use shallow reactive state for lists.

Backend quick wins
- Ensure DRF pagination defaults are set globally and not overridden with huge page sizes.
- Rate limit high-frequency endpoints (notifications/polling).
- Add gzip/brotli only for eligible payload sizes (avoid double compression).

Normalization follow-up
- Frontend still hits legacy paths for client wallet and some older endpoints.
  Move to normalized paths after verifying backend readiness and update cache invalidation rules.
