# Guest Checkout Mock Mode Guide

## 🎭 Overview

The Guest Checkout feature now supports **Mock Mode** for testing and development without requiring a backend connection.

## 🚀 How to Enable Mock Mode

### Option 1: URL Query Parameter
Add `?mock=true` to the URL:
```
http://localhost:5173/guest-checkout?mock=true&website_id=1
```

### Option 2: Environment Variable
Set in `.env` or `.env.local`:
```bash
VITE_USE_MOCK_API=true
```

## ✨ Mock Features

### 1. **Mock Order Configs**
- Paper Types: Essay, Research Paper, Dissertation, Thesis, Case Study
- Academic Levels: High School, Undergraduate, Master's, PhD
- Formatting Styles: APA, MLA, Chicago, Harvard, IEEE
- Types of Work: Writing, Editing, Proofreading, Rewriting
- Subjects: English, Mathematics, Science, History, Business, Psychology

### 2. **Mock Price Calculation**
- Base price: $15 per page
- Academic level multipliers:
  - High School/Undergraduate: 1.0x
  - Master's: 1.2x
  - PhD: 1.5x
- Deadline urgency multipliers:
  - < 24 hours: 1.5x
  - < 48 hours: 1.3x
  - < 72 hours: 1.15x
  - ≥ 72 hours: 1.0x

### 3. **Mock Discount Code**
- **Code**: `TEST10`
- **Discount**: 10% off
- Enter this code in the discount field to test discount functionality

### 4. **Mock Email Verification**
- **50% chance** of requiring email verification
- If verification required, a mock token is generated
- Token format: `mock_token_{timestamp}_{random}`
- Tokens are stored in memory (cleared on page refresh)

### 5. **Mock Order Creation**
- Generates random order IDs (1000-10999)
- Simulates API delays (500ms - 1500ms)
- Returns realistic success/error responses

## 📋 Testing Scenarios

### Scenario 1: Immediate Order Creation
1. Fill out the form
2. Submit order
3. **Expected**: 50% chance order is created immediately (no verification)

### Scenario 2: Email Verification Required
1. Fill out the form
2. Submit order
3. **Expected**: 50% chance verification step appears
4. Copy the verification token from console or use the displayed token
5. Paste token and verify
6. **Expected**: Order created successfully

### Scenario 3: Price Calculation
1. Select paper type
2. Enter number of pages
3. Select academic level
4. Set deadline (try different timeframes)
5. **Expected**: Price updates in real-time sidebar

### Scenario 4: Discount Code
1. Fill out order form
2. Enter discount code: `TEST10`
3. Click "Apply"
4. **Expected**: 10% discount applied, price recalculated

### Scenario 5: Invalid Token
1. Go to verification step
2. Enter invalid token (e.g., "invalid")
3. Click "Verify"
4. **Expected**: Error message displayed

## 🔍 Mock API Responses

### Start Guest Order
```javascript
// With verification
{
  verification_required: true,
  verification_token: "mock_token_1234567890_abc123",
  message: "Verification email sent (mock)"
}

// Without verification
{
  verification_required: false,
  order_id: 5432,
  message: "Order created successfully (mock)"
}
```

### Verify Email
```javascript
{
  order_id: 5432,
  message: "Email verified and order created successfully (mock)"
}
```

### Price Quote
```javascript
{
  total_price: "150.00",
  final_total: "150.00",
  breakdown: {
    base_price: "100.00",
    extra_services: "0.00",
    deadline_multiplier: 1.5,
    discount: "0.00",
    final_total: "150.00"
  }
}
```

## 🎯 Mock Mode Indicator

When mock mode is active, a yellow banner appears at the top:
```
🎭 MOCK MODE - Using simulated data for testing
```

## 🛠️ Development Tips

1. **Console Logging**: Check browser console for mock mode activation
2. **Token Storage**: Mock tokens are stored in memory (Map), cleared on refresh
3. **Realistic Delays**: API calls have simulated delays (500ms - 1500ms)
4. **Error Testing**: Try invalid inputs to test error handling
5. **Price Testing**: Adjust deadline to see different urgency multipliers

## 🔄 Switching Between Mock and Real API

Simply remove `?mock=true` from URL or set `VITE_USE_MOCK_API=false` to use real backend.

## 📝 Notes

- Mock mode is **development/testing only**
- All mock data is stored in memory (not persisted)
- Mock tokens expire on page refresh
- Price calculations are simplified (real backend has more complex logic)
- Discount code `TEST10` is the only mock discount available

## 🐛 Troubleshooting

**Mock mode not activating?**
- Check URL for `?mock=true`
- Check environment variable `VITE_USE_MOCK_API`
- Check browser console for activation message

**Price not calculating?**
- Ensure paper type, pages, and deadline are filled
- Check browser console for errors

**Verification token not working?**
- Tokens are cleared on page refresh
- Make sure you're using the token from the current session
- Check that token format matches: `mock_token_*`

