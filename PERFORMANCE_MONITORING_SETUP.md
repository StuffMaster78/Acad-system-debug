# Performance Monitoring Setup

## ✅ Implementation Complete

A comprehensive performance monitoring system has been set up to track the effectiveness of our optimizations.

---

## 📊 What's Monitored

### 1. **Response Times**
- Average, min, and max response times per endpoint
- Slow endpoint detection (>500ms threshold)
- Real-time performance tracking

### 2. **Query Counts**
- Number of database queries per request
- High query count detection (>10 queries threshold)
- Query optimization tracking

### 3. **Cache Statistics**
- Cache hit/miss rates (if using Redis)
- Cache performance metrics

### 4. **Endpoint Analytics**
- Request counts per endpoint
- Performance trends
- Optimization effectiveness

---

## 🔧 Components

### 1. Middleware (`core/middleware/performance_monitoring.py`)
- Automatically tracks all API requests
- Records response times and query counts
- Stores metrics in cache for dashboard viewing
- Adds performance headers for admin users

### 2. API Endpoints (`admin_management/views/performance_monitoring.py`)

#### Available Endpoints:

**GET `/api/v1/admin/performance/metrics/`**
- Get recent performance metrics for all endpoints
- Shows response times and query counts

**GET `/api/v1/admin/performance/stats/`**
- Get aggregate performance statistics
- Includes cache and database info

**GET `/api/v1/admin/performance/slow-endpoints/?threshold=500`**
- Get endpoints with slow response times
- Default threshold: 500ms

**GET `/api/v1/admin/performance/high-query-endpoints/?threshold=10`**
- Get endpoints with high query counts
- Default threshold: 10 queries

**POST `/api/v1/admin/performance/clear-metrics/`**
- Clear all performance metrics (admin only)

---

## 📈 Usage

### View Performance Metrics

```bash
# Get all metrics
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/v1/admin/performance/metrics/

# Get slow endpoints
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/v1/admin/performance/slow-endpoints/?threshold=1000

# Get high query endpoints
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/v1/admin/performance/high-query-endpoints/?threshold=20
```

### Response Headers (Admin Users)

Admin users will see performance headers in API responses:
- `X-Response-Time`: Response time in milliseconds
- `X-Query-Count`: Number of database queries

---

## 📊 Expected Results After Optimization

### Before Optimization:
- Dashboard endpoints: 150-300ms, 15-30 queries
- List endpoints: 200-500ms, 20-50 queries
- High query counts on filtered searches

### After Optimization:
- Dashboard endpoints: 30-50ms, 1-3 queries (cached: 5ms)
- List endpoints: 50-100ms, 5-10 queries
- Reduced query counts on all endpoints

---

## 🎯 Monitoring Dashboard (Future Enhancement)

You can create a frontend dashboard component to visualize:
- Response time trends
- Query count trends
- Slow endpoint alerts
- Cache hit rates
- Optimization effectiveness

---

## 🔍 Logging

The middleware logs:
- **WARNING**: Requests > 1 second
- **WARNING**: Requests with > 20 queries

Check logs for:
```
Slow request: GET /api/v1/admin/dashboard/ - 1200.50ms, 25 queries
High query count: GET /api/v1/orders/ - 15 queries in 250.30ms
```

---

## ⚙️ Configuration

### Adjust Thresholds

Edit `core/middleware/performance_monitoring.py`:
- Slow request threshold: `response_time > 1000` (1 second)
- High query threshold: `query_count > 20`

### Cache Duration

- Recent metrics: 1 hour (last 100 requests per endpoint)
- Aggregate stats: 24 hours

---

## ✅ Verification

1. **Check middleware is active:**
   ```bash
   # Make API requests and check response headers
   curl -I -H "Authorization: Bearer <admin_token>" \
     http://localhost:8000/api/v1/admin/dashboard/
   ```

2. **View metrics:**
   ```bash
   curl -H "Authorization: Bearer <admin_token>" \
     http://localhost:8000/api/v1/admin/performance/stats/
   ```

3. **Check logs:**
   - Look for performance warnings in Django logs
   - Monitor slow endpoint alerts

---

## 📝 Notes

- Metrics are stored in cache (Redis recommended)
- Only tracks `/api/` requests (not static files)
- Admin users see performance headers automatically
- Metrics are aggregated per endpoint
- Can be cleared via API endpoint

---

## 🚀 Next Steps

1. **Create Frontend Dashboard** - Visualize metrics
2. **Set Up Alerts** - Notify on slow endpoints
3. **Historical Tracking** - Store metrics in database
4. **Performance Reports** - Weekly/monthly summaries

---

**Status:** ✅ **ACTIVE AND MONITORING**

