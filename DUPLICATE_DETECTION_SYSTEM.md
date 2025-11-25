# Duplicate Account Detection System - Complete ✅

## Overview
A comprehensive system to detect suspected duplicate accounts across multiple websites in the multi-tenant platform. Helps identify clients and writers who may have created multiple accounts using different credentials.

## 🎯 Problem Statement
In a multi-tenant system, users (especially clients) might create multiple accounts across different websites to:
- Get multiple discounts or referral bonuses
- Bypass restrictions or limits
- Create fake reviews or ratings
- Abuse the system in other ways

Writers might also create multiple accounts to:
- Bypass restrictions or limits
- Get more orders than allowed
- Operate under different identities

## ✅ Backend Implementation

### 1. Duplicate Detection Service
**File:** `backend/admin_management/services/duplicate_detection.py`

**Detection Methods:**

#### a. Email Similarity Detection
- Normalizes emails (removes dots, lowercases)
- Detects accounts with same normalized email
- Example: `user@gmail.com` and `user+1@gmail.com` → same normalized email
- **Confidence:** High

#### b. IP Address Overlap
- Analyzes login sessions and IP logs
- Identifies accounts sharing same IP addresses
- Looks at last 90 days of activity
- **Confidence:** Medium (IPs can be shared legitimately)

#### c. Name Similarity
- Compares first and last names
- Uses similarity scoring algorithm
- Detects accounts with similar names (>70% similarity)
- **Confidence:** Medium to Low (names can be similar by coincidence)

#### d. Cross-Website Activity Patterns
- Detects users active across multiple websites
- Matches email patterns across websites
- Identifies potential multi-account users
- **Confidence:** High

### 2. API Endpoints
**Base URL:** `/api/v1/admin-management/duplicate-detection/`

**Endpoints:**
- `GET /detect/` - Run full duplicate detection
  - Query params: `role` (client/writer), `min_confidence` (low/medium/high), `limit`
- `GET /by-role/{role}/` - Get duplicates for specific role
- `GET /{user_id}/user-duplicates/` - Get duplicates for specific user
- `GET /stats/` - Get statistics about duplicates

**Response Format:**
```json
{
  "count": 10,
  "results": [
    {
      "user_ids": [1, 2],
      "users": [
        {
          "id": 1,
          "username": "user1",
          "email": "user1@example.com",
          "role": "client",
          "website": {"id": 1, "name": "Website 1"},
          "date_joined": "2024-01-01T00:00:00Z",
          "is_active": true
        }
      ],
      "websites": [{"id": 1, "name": "Website 1"}],
      "signals": ["Same normalized email: user@example.com", "Shared IP address: 192.168.1.1"],
      "detection_types": ["email", "ip_address"],
      "confidence": "high",
      "match_count": 2
    }
  ]
}
```

## ✅ Frontend Implementation

### Component: Duplicate Account Detection
**Route:** `/admin/duplicate-detection`
**File:** `frontend/src/views/admin/DuplicateAccountDetection.vue`

**Features:**

1. **Detection Dashboard:**
   - Stats cards showing suspected groups
   - Separate counts for clients and writers
   - Total users involved

2. **Filtering Options:**
   - Filter by role (client/writer/all)
   - Filter by confidence level (low/medium/high)
   - Filter by detection type (email/IP/name/cross-website)
   - Reset filters

3. **Results Table:**
   - Shows all suspected duplicate groups
   - Displays users in each group
   - Shows websites involved
   - Lists detection signals
   - Shows confidence level
   - Quick actions (view details, mark as reviewed)

4. **Detail Modal:**
   - Full information about suspected duplicates
   - Side-by-side user comparison
   - All detection signals listed
   - Confidence explanation and recommendations
   - Links to view full user profiles

5. **User Guidance:**
   - Clear explanations of how detection works
   - Warnings about false positives
   - Recommendations based on confidence level
   - Action buttons for reviewing users

## 🔍 Detection Signals Explained

### High Confidence Signals:
- **Email Similarity: Same normalized email**
  - Most reliable indicator
  - Gmail-style emails (user@gmail.com = u.s.e.r@gmail.com)
  - Different email providers but same base

- **Cross-Website Activity: Same email pattern across sites**
  - User active on multiple websites with matching credentials
  - Strong indicator of intentional multi-account creation

### Medium Confidence Signals:
- **IP Address Overlap: Shared IP addresses**
  - Multiple accounts logging in from same IP
  - Could be legitimate (family, office, VPN)
  - More reliable when combined with other signals

- **Name Similarity: Similar first and last names**
  - Names match >80% similarity
  - Could be family members or coincidence
  - Less reliable alone

### Low Confidence Signals:
- **Name Similarity: Moderate similarity (70-80%)**
  - Some name overlap
  - Often false positives
  - Requires additional investigation

## 📊 How to Use

### For Admins/Superadmins:

1. **Run Detection:**
   - Click "Run Detection" button
   - System scans all users across all websites
   - Results appear in the table

2. **Review Results:**
   - Start with "High Confidence" duplicates
   - Review each group carefully
   - Check user activity, orders, payments
   - Look for patterns

3. **Investigate:**
   - Click "Details" to see full information
   - View user profiles to compare activity
   - Check if accounts are actually duplicates
   - Consider legitimate reasons (family, business)

4. **Take Action:**
   - If confirmed duplicates:
     - Suspend or blacklist duplicate accounts
     - Merge accounts if appropriate
     - Contact users if needed
   - If false positives:
     - Mark as reviewed
     - System will remember (future enhancement)

## ⚠️ Important Considerations

### False Positives:
- **Shared IPs:** Family members, office networks, VPNs
- **Similar Names:** Common names, family members
- **Legitimate Multi-Accounts:** Business accounts, team accounts

### Best Practices:
1. **Always Investigate:** Don't take action based solely on detection
2. **Check Activity:** Review order history, payment methods, behavior
3. **Consider Context:** Some multi-accounts may be legitimate
4. **Document Decisions:** Keep notes on why accounts were/weren't merged
5. **Contact Users:** When in doubt, reach out to users for clarification

## 🔧 Technical Details

### Detection Algorithm:
1. Runs all detection methods in parallel
2. Groups results by user sets
3. Aggregates signals and confidence levels
4. Filters by role and confidence if specified
5. Returns grouped results

### Performance:
- Email detection: O(n) - Fast
- IP detection: O(n*m) - Moderate (n=users, m=IPs)
- Name similarity: O(n²) - Slower for large datasets
- Cross-website: O(n) - Fast

**Optimization Tips:**
- Use `min_confidence` filter to reduce results
- Use `role` filter to focus on specific user types
- Use `limit` to cap results for initial review

## 🚀 Future Enhancements

1. **Automatic Review Tracking:**
   - Store reviewed duplicates in database
   - Don't show already-reviewed groups
   - Track admin decisions

2. **Merge Functionality:**
   - UI to merge duplicate accounts
   - Transfer orders, payments, history
   - Preserve important data

3. **Machine Learning:**
   - Learn from admin decisions
   - Improve confidence scoring
   - Reduce false positives

4. **Real-time Monitoring:**
   - Alert when new duplicates detected
   - Monitor specific users
   - Dashboard widgets

5. **Payment Method Detection:**
   - Analyze payment cards
   - Detect shared payment methods
   - Higher confidence when combined

## ✅ All Features Complete

- ✅ Multi-signal detection (email, IP, name, cross-website)
- ✅ Confidence scoring (low, medium, high)
- ✅ Role-based filtering
- ✅ Comprehensive frontend UI
- ✅ Detailed user information
- ✅ Clear explanations and guidance
- ✅ Statistics dashboard
- ✅ User profile integration

The duplicate detection system is now fully functional and ready to help identify multi-account users!

