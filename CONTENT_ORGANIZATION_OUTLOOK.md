# Content Organization Outlook - Multi-Website System

## Overview

This document outlines how content (Blog Posts, SEO Pages, Categories, Tags, etc.) is organized and displayed across different client websites in the multi-tenant system.

---

## 🏗️ Architecture: Multi-Tenant Content System

### Core Principle
**Every piece of content belongs to a specific website.** This ensures complete data isolation between different client websites while allowing superadmins to manage content across all websites.

### Database Structure

```
Website (Tenant)
├── Blog Posts
│   ├── Categories (scoped to website)
│   ├── Tags (scoped to website)
│   ├── Authors (scoped to website)
│   └── Media Assets (scoped to website)
├── SEO Pages
│   ├── Content Blocks
│   └── Templates
├── Media Library
└── Analytics & Metrics
```

---

## 📋 Content Listing Structure

### 1. **Admin Dashboard View** (`/admin/blog`)

#### Current Implementation
- **Table View** with columns:
  - Title & Slug
  - **Website** (name + domain) ← Key identifier
  - Category
  - Status (Draft/Published/Archived)
  - Author(s)
  - Engagement Metrics (Views, Likes)
  - Published Date
  - Actions (View, Edit, Publish, Delete)

#### Filtering Options
- **Category Filter**: Shows categories for all accessible websites
- **Status Filter**: Draft, Published, Archived
- **Search**: By title/slug
- **Tab Views**:
  - All Posts
  - My Drafts
  - Needs Review
  - Scheduled
  - Stale Published

#### Website Filtering Logic

**For Regular Admins:**
- Only see content from their assigned website
- Cannot switch between websites
- Website column shows their website (for consistency)

**For Superadmins:**
- See content from ALL websites
- Can filter by website (if filter added)
- Website column shows which website each post belongs to
- Can create/edit content for any website

---

## 🎯 Proposed Enhanced Content Listing

### Option A: Website-First Organization (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│  Content Management Dashboard                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Website Selector Dropdown] ──────────────── [Create New] │
│  ▼ All Websites                                              │
│    • Client A Website (example.com)                         │
│    • Client B Website (example2.com)                         │
│    • Client C Website (example3.com)                         │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📊 Website: Client A Website                                │
│  🌐 Domain: example.com                                      │
│  📈 Stats: 45 Posts | 12 Categories | 8 Authors              │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Tabs: [Posts] [Categories] [Tags] [Authors] [Analytics]     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Filters: [Category ▼] [Status ▼] [Search...] [Reset]       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Title          │ Category │ Status │ Author │ Date  │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Blog Post 1    │ Tech     │ Pub    │ John   │ ...  │   │
│  │ Blog Post 2    │ Health   │ Draft  │ Jane   │ ...  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Clear website context
- Easy to switch between websites
- Website-specific stats visible
- Prevents accidental cross-website operations

---

### Option B: Unified View with Website Grouping

```
┌─────────────────────────────────────────────────────────────┐
│  Content Management - All Websites                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  🔍 [Search All Content...]  [Website Filter ▼] [Status ▼] │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📌 Client A Website (example.com)                   │   │
│  │ ─────────────────────────────────────────────────── │   │
│  │ • Blog Post 1 - Tech Category - Published          │   │
│  │ • Blog Post 2 - Health Category - Draft            │   │
│  │                                                      │   │
│  │ 📌 Client B Website (example2.com)                  │   │
│  │ ─────────────────────────────────────────────────── │   │
│  │ • Blog Post 3 - Business Category - Published      │   │
│  │ • Blog Post 4 - Finance Category - Scheduled       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- See all content at once
- Easy comparison across websites
- Good for superadmins managing multiple sites

---

### Option C: Dashboard with Website Cards

```
┌─────────────────────────────────────────────────────────────┐
│  Content Management Dashboard                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Client A     │  │ Client B     │  │ Client C     │     │
│  │ Website      │  │ Website      │  │ Website      │     │
│  │              │  │              │  │              │     │
│  │ 📝 45 Posts  │  │ 📝 32 Posts  │  │ 📝 18 Posts  │     │
│  │ 📂 12 Cats   │  │ 📂 8 Cats    │  │ 📂 5 Cats     │     │
│  │ 👤 8 Authors │  │ 👤 5 Authors │  │ 👤 3 Authors  │     │
│  │              │  │              │  │              │     │
│  │ [View All]   │  │ [View All]   │  │ [View All]   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  Clicking a card navigates to that website's content list   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Visual overview of all websites
- Quick access to website-specific content
- Great for superadmins with many websites

---

## 🔐 Permission-Based Content Access

### Regular Admin (Assigned to One Website)
```
Access Level: Single Website
├── Can only see content from their website
├── Cannot view other websites' content
├── Cannot create content for other websites
└── Website selector hidden or disabled
```

### Superadmin (Manages All Websites)
```
Access Level: All Websites
├── Can see content from all websites
├── Can switch between websites
├── Can create/edit content for any website
└── Website selector shows all active websites
```

---

## 📊 Content Metrics Per Website

### Website-Level Analytics
Each website has its own metrics dashboard:

```
Website: Client A Website
├── Content Metrics
│   ├── Total Posts: 45
│   ├── Published: 38
│   ├── Drafts: 7
│   └── Categories: 12
├── Engagement Metrics
│   ├── Total Views: 12,450
│   ├── Total Likes: 890
│   └── Avg. Engagement: 7.1%
├── SEO Health
│   ├── Posts with Good SEO: 32/38
│   └── Average Score: 85/100
└── Publishing Trends
    ├── This Month: 8 posts
    └── Target: 12 posts
```

---

## 🌐 Public-Facing Content Display

### Blog Post Listing (`/blog` or `/blogs`)
Content is automatically filtered by website based on:
1. **Domain-based routing**: `example.com/blog` shows only that website's posts
2. **Website ID in URL**: `/blog?website_id=1` explicitly filters
3. **Session/User context**: If user is logged in, show their website's content

### SEO Pages Listing
Similar filtering:
- Domain-based: `example.com/services` shows that website's service pages
- Category-based: `example.com/services/web-design` filters by category

---

## 🗂️ Content Organization Hierarchy

### Per Website Structure

```
Website: Client A
│
├── 📝 Blog Posts (45)
│   ├── Category: Technology (12 posts)
│   │   ├── Tag: Web Development (5 posts)
│   │   ├── Tag: Mobile Apps (4 posts)
│   │   └── Tag: AI/ML (3 posts)
│   ├── Category: Health (18 posts)
│   │   ├── Tag: Nutrition (8 posts)
│   │   └── Tag: Fitness (10 posts)
│   └── Category: Business (15 posts)
│       └── Tag: Marketing (15 posts)
│
├── 🌐 SEO Pages (23)
│   ├── Service Pages (15)
│   └── Landing Pages (8)
│
├── 📁 Media Library (156 assets)
│   ├── Images (120)
│   ├── Videos (25)
│   └── Documents (11)
│
├── 👥 Authors (8)
│   ├── John Doe (15 posts)
│   ├── Jane Smith (12 posts)
│   └── ...
│
└── 📊 Analytics
    ├── Content Performance
    ├── SEO Health
    └── Engagement Metrics
```

---

## 🔄 Content Workflow Per Website

### Creation Flow
1. **Select Website** (if superadmin) or auto-assigned (if regular admin)
2. **Create Content** (Blog Post, SEO Page, etc.)
3. **Assign to Category/Tag** (from that website's categories/tags)
4. **Assign Authors** (from that website's authors)
5. **Publish** → Content appears on that website's public site

### Editing Flow
1. **Filter by Website** (if needed)
2. **Select Content** to edit
3. **Edit** → Changes apply only to that website's content
4. **Save** → Updates reflected on that website

---

## 📱 Recommended UI Enhancements

### 1. Website Switcher Component
```vue
<WebsiteSwitcher 
  :websites="availableWebsites"
  :current-website="selectedWebsite"
  @switch="handleWebsiteSwitch"
/>
```

### 2. Website Context Banner
```vue
<WebsiteContextBanner 
  :website="currentWebsite"
  :stats="websiteStats"
/>
```

### 3. Website-Scoped Filters
- Categories dropdown shows only current website's categories
- Tags dropdown shows only current website's tags
- Authors dropdown shows only current website's authors

---

## 🎨 Visual Indicators

### Website Badge
Each content item should display:
- Website name (if viewing all websites)
- Website domain (subtle, secondary text)
- Website color/logo (if available)

### Status Indicators
- 🟢 Active website
- 🔴 Inactive website
- 🟡 Website with issues

---

## 📈 Future Enhancements

### 1. Bulk Operations Per Website
- Bulk publish/unpublish for a website
- Bulk category assignment
- Bulk author assignment

### 2. Website Templates
- Clone content structure from one website to another
- Apply website-specific templates

### 3. Cross-Website Analytics
- Compare performance across websites
- Aggregate metrics for all websites

### 4. Website-Specific Settings
- Default authors per website
- Default categories per website
- Publishing schedules per website

---

## 🔍 Search & Filtering

### Global Search (Superadmin)
- Search across all websites
- Results grouped by website
- Filter results by website

### Website-Scoped Search (Regular Admin)
- Search only within their website
- Faster, more focused results

---

## 📝 Summary

**Key Points:**
1. ✅ Every content item is tied to a specific website
2. ✅ Admins see only their website's content (unless superadmin)
3. ✅ Superadmins can manage all websites
4. ✅ Public sites show only their website's content
5. ✅ Categories, tags, authors are scoped per website
6. ✅ Analytics and metrics are per-website

**Current State:**
- ✅ Backend fully supports multi-website content
- ✅ Frontend shows website column in listings
- ✅ Website selection available in create/edit forms
- ⚠️ Could benefit from website-first navigation

**Recommended Next Steps:**
1. Add website selector/switcher to admin views
2. Implement website context banner
3. Add website-scoped filtering
4. Create website dashboard cards view
5. Enhance website indicators in content lists

