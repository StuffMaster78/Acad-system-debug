Endpoint Audit (API v1)

Generated: 2026-01-19

Base
- API root: /api/v1/
- Schema/docs: /api/v1/schema/, /api/v1/docs/swagger/, /api/v1/docs/redoc/
- Health: /health/, /health/ready/, /health/live/

Core
- /api/v1/dropdown-options/
- /api/v1/dashboard-config/
- /api/v1/config-versioning/

Auth & Users
- /api/v1/auth/ (auth, MFA/OTP, sessions, magic links, unlock, password reset)
- /api/v1/users/ (users, account, privacy, gdpr, security activity, login alerts, profile changes, subscriptions)

Orders
- /api/v1/orders/
  Resources: orders, disputes, writer-request, order-requests, reassignment-logs, progress,
  draft-requests, draft-files, templates, order-drafts, order-presets, revision-requests,
  writer-acknowledgments, writer-assignment-acceptances, preferred-writer-responses,
  message-reminders, review-reminders, guest-orders, assignment-analytics
  Custom: orders/<id>/action(s)/..., logs, extend-deadline, admin editing, webhooks

Communications
- /api/v1/order-communications/
  Resources: communication-threads, communication-notifications, screened-words, flagged-messages, dispute-messages
  Custom: thread messages, attachments, typing, SSE streams

Order Files
- /api/v1/order-files/
  Resources: order-files, file-deletion-requests, external-links, extra-service-files,
  order-files-config, file-categories, download-logs, style-reference-files

Order Payments
- /api/v1/order-payments/
  Resources: order-payments, transactions, payment-notifications, payment-logs,
  payment-disputes, discount-usage, admin-logs, payment-reminder-settings,
  payment-reminder-configs, payment-deletion-messages, payment-reminders-sent,
  payments, invoices
  Webhooks: /api/v1/order-payments/webhooks/payment|stripe|paypal/

Special Orders (normalized)
- /api/v1/special-orders/
  Resources: special-orders, streamlined-orders, installment-payments,
  predefined-special-order-configs, predefined-special-order-durations,
  writer-bonuses, estimated-special-order-settings, special-order-inquiry-files
  Legacy alias: /api/v1/special-orders/api/

Class Management
- /api/v1/class-management/
  Resources: class-bundles, class-purchases, class-installments, class-bundle-configs,
  express-classes, class-payments, express-class-inquiry-files

Tickets
- /api/v1/tickets/
  Resources: tickets, messages, logs, statistics, attachments, sla

Wallets
- /api/v1/wallet/ (system wallet)
  Resources: wallets, wallets/top-up, wallets/withdraw, withdrawal-requests
- /api/v1/client-wallet/ (client wallet)
  Resources: client-wallet, loyalty-transactions, referral-bonuses, referral-stats, admin/wallets
  Legacy alias: /api/v1/wallet/api/
- /api/v1/writer-wallet/ (writer wallet)
  Resources: writer-wallets, wallet-transactions, payment-batches, payment-schedules,
  scheduled-payments, payment-order-records, writer-payments, payment-adjustments,
  payment-confirmations, payment-requests
- /api/v1/writer-payments/
  Resources: payment-management

Admin / Support / Editor / Superadmin
- /api/v1/admin-management/
  Resources: dashboard, users, activity-logs, user-management, configs/*, emails/*,
  disputes (+ dashboard), refunds (+ dashboard), reviews (+ dashboard), orders (+ dashboard),
  fines (+ dashboard), advanced-analytics, geographic-analytics, writer-assignment,
  express-classes/dashboard, class-bundles(+dashboard), special-orders(+dashboard),
  advance-payments/dashboard, tips, financial-overview, unified-search, exports,
  duplicate-detection, referrals/*, loyalty/tracking, system-health, performance,
  rate-limiting, compression
- /api/v1/support-management/
  Resources: support-profiles, notifications, order-management, messages, escalations,
  workload-tracker, payment-issues, faqs, dashboard, disputes, dispute-messages
- /api/v1/editor-management/
  Resources: profiles, tasks, reviews, notifications, performance, admin-assignments
- /api/v1/superadmin-management/
  Resources: superadmin-profile, users, logs, dashboard, appeals, tenants

Notifications
- /api/v1/notifications/
  Resources: notifications, in-app-notifications, notification-preferences, preferences,
  admin/notifications, notification-profiles, notification-groups, notification-group-profiles,
  broadcast-notifications, event-preferences, role-defaults, notifications/feed,
  notifications/status, my/event-preferences, webhook-endpoints
  Custom: notifications/meta, list/detail/mark-read, unread-count, preview-email,
  SSE stream, polling, feed, mark-read, bulk mark all, templates preview

Discounts / Referrals / Refunds / Fines / Loyalty / Reviews
- /api/v1/discounts/
  Resources: discounts, discount-usage, discount-stacking-rules, promotional-campaigns, seasonal-events
  Custom: discounts/analytics, discounts/analytics/campaign-analytics/<id>/
- /api/v1/referrals/
  Resources: referrals, referral-bonus-configs, referral-admin, referral-codes,
  referral-stats, referral-bonus-decays
  Custom: referral-reports, award-referral-bonus/<id>/
- /api/v1/refunds/
  Resources: refunds, refund-logs, refund-receipts
- /api/v1/fines/
  Resources: fines, fine-appeals, lateness-rules, fine-types
  Legacy alias: /api/v1/fines/api/
- /api/v1/loyalty-management/
  Resources: loyalty-tiers, loyalty-transactions, milestones, client-badges,
  loyalty-points-conversion-config, redemption-categories, redemption-items,
  redemption-requests, analytics, dashboard-widgets
  Custom: loyalty/summary, loyalty/convert, loyalty/transactions, admin/force-convert,
  admin/award-loyalty, admin/loyalty-conversion-config, admin/transfer-loyalty, admin/deduct-loyalty
- /api/v1/reviews/
  Resources: website-reviews, writer-reviews, order-reviews, aggregation

Announcements / Activity / Analytics / Holidays
- /api/v1/announcements/ (announcements)
- /api/v1/activity/ (activity-logs, user-feed)
- /api/v1/analytics/ (client, writer, class, content-events)
- /api/v1/holidays/ (special-days, reminders, campaigns)

Websites / CMS / Media
- /api/v1/websites/
  Resources: websites, website-logs, static-pages, branding, feature-toggles, integrations
  Custom: websites/<id>/update_seo_settings, soft_delete, restore
- /api/v1/blog_pages_management/
  Resources: blogs, categories, tags, authors, newsletters, newsletter-subscribers,
  newsletter-analytics, blog-media, blog-videos, blog-dark-mode-images, ab-tests,
  clicks, conversions, social-platforms, blog-shares, cta-blocks, cta-placements,
  content-block-templates, content-blocks, edit-history, seo-metadata, faq-schemas,
  author-schemas, pdf-sample-sections, pdf-samples, pdf-sample-downloads, blog-revisions,
  blog-autosaves, blog-edit-locks, blog-previews, internal-preview, blog-workflows,
  review-comments, workflow-transitions, content-templates, content-snippets,
  editor-tooling, editor-sessions, editor-productivity, editor-analytics, blog-analytics,
  content-metrics, content-audit, media-browser, website-metrics, publishing-targets,
  category-publishing-targets, content-freshness-reminders, content-calendar
  Custom: admin-notifications, blogs restore/delete, robots/sitemap, preview
- /api/v1/service-pages/
  Resources: service-pages, service-page-pdf-sample-sections, service-page-pdf-samples, service-website-metrics
- /api/v1/seo-pages/
  Resources: seo-pages
  Public: /api/v1/public/seo-pages/, /api/v1/public/seo-pages/<slug>/
- /api/v1/media/
  Resources: media-assets, media-usages

Mass Email
- /api/v1/mass-emails/
  Resources: campaigns, recipients, attachments, templates, providers
  Custom: track/open, track/click, unsubscribe, analytics/campaigns, analytics/trending,
  email-history, admin/email-history

Normalization changes
- Removed internal "/api/" prefixes inside apps and added legacy aliases at:
  /api/v1/order-configs/api/, /api/v1/special-orders/api/, /api/v1/fines/api/,
  /api/v1/wallet/api/ (client wallet legacy)

Potential gaps
- pricing app is installed but not exposed via URLs (no /api/v1/pricing/).
- Some paths remain legacy in frontend (see PERFORMANCE_FIXLIST.md notes).
