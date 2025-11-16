# Location Info Endpoint ✅

## Summary

Added a new endpoint to get user's location information (country) on the fly based on their session info and real-time IP geolocation.

## ✅ New Endpoint

### GET `/api/v1/users/location-info/`

**Description**: Get user's location information including country from multiple sources.

**Authentication**: Required (IsAuthenticated)

**Response Format**:
```json
{
  "ip_address": "192.168.1.1",
  "user_selected_country": "US",
  "detected_country": "US",
  "current_country": "US",
  "session_country": "US",
  "timezone": "America/New_York",
  "country_source": "user_selected"
}
```

**Response Fields**:
- `ip_address` (string): Current IP address from request
- `user_selected_country` (string|null): Country selected by user in their profile
- `detected_country` (string|null): Country detected from IP (stored in User model)
- `current_country` (string|null): Country detected from current IP (real-time)
- `session_country` (string|null): Country from current active session
- `timezone` (string|null): Timezone detected from IP
- `country_source` (string): Source of the country data:
  - `"user_selected"` - User manually selected country
  - `"session"` - From current session
  - `"detected"` - From stored detected country
  - `"current_ip"` - From real-time IP geolocation
  - `"unknown"` - No country data available

## 📍 Data Sources

The endpoint retrieves country information from multiple sources in priority order:

1. **UserProfile.country** - User-selected country (highest priority)
2. **UserSession.country** - Country detected during login session
3. **User.detected_country** - Country detected from IP (stored in User model)
4. **Real-time IP geolocation** - Country detected from current IP address

## 🔧 Implementation Details

### Backend Changes

**File**: `users/views.py`

Added new action method:
```python
@action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
def location_info(self, request):
    """
    Get user's location information including country.
    Returns country from multiple sources:
    - User-selected country (from UserProfile)
    - Detected country (from User.detected_country or real-time detection)
    - Current session country (from UserSession if available)
    - Current IP address
    """
```

**Features**:
- ✅ Gets IP address from request headers (handles proxies)
- ✅ Retrieves user-selected country from UserProfile
- ✅ Gets detected country from User model (GeoDetectionMixin)
- ✅ Performs real-time IP geolocation if needed
- ✅ Retrieves country from current active session
- ✅ Returns timezone information
- ✅ Indicates the source of country data

### GeoDetectionMixin Enhancement

**File**: `users/mixins.py`

Updated `auto_detect_country()` method to save detected country:
- Now saves detected country to database
- Uses ipinfo.io API for geolocation
- Handles errors gracefully

## 🎯 Usage Examples

### Frontend Usage

```javascript
// Get location info
const response = await apiClient.get('/users/location-info/')
const locationData = response.data

console.log('Country:', locationData.current_country)
console.log('Source:', locationData.country_source)
console.log('IP:', locationData.ip_address)
console.log('Timezone:', locationData.timezone)
```

### Vue.js Component Example

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'

const authStore = useAuthStore()
const locationInfo = ref(null)
const loading = ref(false)

const fetchLocationInfo = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/users/location-info/')
    locationInfo.value = response.data
  } catch (error) {
    console.error('Failed to fetch location info:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchLocationInfo()
  }
})
</script>

<template>
  <div v-if="locationInfo">
    <p>Country: {{ locationInfo.current_country }}</p>
    <p>Source: {{ locationInfo.country_source }}</p>
    <p>IP: {{ locationInfo.ip_address }}</p>
    <p>Timezone: {{ locationInfo.timezone }}</p>
  </div>
</template>
```

## 🔒 Security & Privacy

- ✅ Only authenticated users can access this endpoint
- ✅ IP address is extracted from request headers (handles proxies)
- ✅ No sensitive user data is exposed
- ✅ Country detection is done server-side (more accurate)
- ✅ Real-time detection only when needed (cached when possible)

## 📝 Notes

- The endpoint uses **ipinfo.io** API for geolocation (free tier available)
- Country detection is cached in the User model (`detected_country` field)
- Real-time detection is performed only if cached data is not available
- Session country is retrieved from `UserSession` model if available
- User-selected country takes priority over detected country

## ✅ Status

**Endpoint Created**: ✅
**Backend Implementation**: ✅
**Ready for Frontend Integration**: ✅

---

**Last Updated**: 2024-12-19  
**Status**: ✅ Complete - Ready to Use

