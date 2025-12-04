# Next Features Priority List

Based on current implementation status, here are the recommended next features to implement:

## 🔴 High Priority (Core Functionality Gaps)

### 1. **Public Blog/SEO Page Components** (0% Complete)
**Status**: Backend APIs exist, but no public-facing frontend components
**What's Needed**:
- `frontend/src/views/public/BlogPost.vue` - Public blog post display page
- `frontend/src/views/public/SeoPage.vue` - Public SEO landing page display
- Integration with engagement tracker (views, scroll, likes/dislikes)
- Author strips component for displaying author info
- Related content widgets
- SEO meta tags rendering

**Impact**: Critical - Without this, published content isn't accessible to end users
**Estimated Effort**: Medium (2-3 days)

### 2. **Guest Checkout Frontend UI** (0% Complete)
**Status**: Backend endpoints ready (`/guest-orders/start`, `/guest-orders/verify-email`)
**What's Needed**:
- `frontend/src/views/guest/GuestCheckout.vue` - Main guest checkout flow
- `frontend/src/components/guest/EmailVerification.vue` - Email verification step
- Order form for guests (similar to regular order form but simplified)
- Integration with `ordersAPI.startGuestOrder()` and `ordersAPI.verifyGuestEmail()`

**Impact**: High - Enables anonymous order placement
**Estimated Effort**: Medium (2-3 days)

### 3. **Media Library Frontend UI** (0% Complete)
**Status**: Backend API exists (`/api/v1/media/media-assets/`)
**What's Needed**:
- `frontend/src/views/admin/MediaLibrary.vue` - Media browser/manager
- `frontend/src/components/media/MediaPicker.vue` - Reusable media picker component
- Upload functionality
- Filter by type (image, video, document)
- Search and tag filtering
- Integration into blog/SEO page editors

**Impact**: High - Needed for content creation workflow
**Estimated Effort**: Medium (2-3 days)

## 🟡 Medium Priority (Enhancement Features)

### 4. **Block Editor for SEO Pages** (0% Complete)
**Status**: SEO pages have `blocks` JSONField, but no visual editor
**What's Needed**:
- `frontend/src/components/editor/BlockEditor.vue` - Visual block-based editor
- Block types: paragraph, heading, image, CTA, table, etc.
- Drag-and-drop block reordering
- Block configuration modals
- Preview mode

**Impact**: Medium - Improves content creation UX
**Estimated Effort**: High (4-5 days)

### 5. **Author Strips Component** (0% Complete)
**Status**: Author data exists, but no display component
**What's Needed**:
- `frontend/src/components/blog/AuthorStrip.vue` - Display author info with photo, bio, social links
- Integration into public blog post pages
- Schema.org Person markup rendering

**Impact**: Medium - Improves SEO and user trust
**Estimated Effort**: Low (1 day)

### 6. **Engagement UI Components** (0% Complete)
**Status**: Tracking backend exists, but no UI for users to interact
**What's Needed**:
- `frontend/src/components/engagement/LikeDislikeButtons.vue` - Like/dislike buttons
- `frontend/src/components/engagement/EngagementStats.vue` - Display view counts, likes, etc.
- Integration into public blog/SEO pages
- Real-time updates (optional)

**Impact**: Medium - Enables user engagement
**Estimated Effort**: Low (1-2 days)

## 🟢 Low Priority (Nice to Have)

### 7. **Analytics Dashboard for Content** (30% Complete)
**Status**: Basic analytics exist, but no visualization
**What's Needed**:
- `frontend/src/views/admin/ContentAnalytics.vue` - Analytics dashboard
- Charts for views, engagement, scroll depth
- Top performing content
- Time-based analytics

**Impact**: Low - Useful for optimization but not critical
**Estimated Effort**: Medium (2-3 days)

### 8. **Block Editor for Blogs** (0% Complete)
**Status**: Blogs use rich text editor, but could benefit from block editor
**What's Needed**:
- Similar to SEO page block editor
- Migration path from rich text to blocks
- Backward compatibility

**Impact**: Low - Enhancement, not critical
**Estimated Effort**: High (4-5 days)

---

## 📋 Recommended Implementation Order

1. **Public Blog/SEO Page Components** (High Priority)
   - Enables content to be viewed by end users
   - Foundation for engagement tracking

2. **Guest Checkout Frontend UI** (High Priority)
   - Completes the guest checkout feature
   - Enables revenue generation

3. **Media Library Frontend UI** (High Priority)
   - Essential for content creation workflow
   - Needed for blog/SEO page editors

4. **Author Strips Component** (Medium Priority)
   - Quick win, improves SEO
   - Enhances user trust

5. **Engagement UI Components** (Medium Priority)
   - Enables user interaction
   - Completes engagement tracking feature

6. **Block Editor for SEO Pages** (Medium Priority)
   - Improves content creation UX
   - More complex, can be done later

---

## 🎯 Quick Wins (Can be done in parallel)

- Author Strips Component (1 day)
- Engagement UI Components (1-2 days)
- Basic Analytics Dashboard (2-3 days)

---

## 💡 Notes

- All backend APIs are ready for these features
- Frontend API clients are already created
- Focus on public-facing components first (revenue impact)
- Admin UI enhancements can follow

