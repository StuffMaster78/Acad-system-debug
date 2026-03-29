# Deployment Checklist
## Tip Management & Loyalty Redemption Systems

This checklist ensures a safe and successful deployment of the Tip Management and Loyalty Redemption features.

---

## Pre-Deployment Checklist

### 1. Database Migrations

#### ✅ Verify All Migrations Are Created
- [ ] `writer_management/migrations/0002_add_tip_model.py` - Tip model with all fields
- [ ] `loyalty_management/migrations/0003_alter_clientbadge_unique_together_and_more.py` - Redemption models
- [ ] `loyalty_management/migrations/0004_add_redemptionitem_missing_fields.py` - Missing fields
- [ ] `loyalty_management/migrations/0005_add_min_tier_level.py` - Min tier level field
- [ ] `class_management/migrations/0005_alter_classinstallment_options_and_more.py` - Class installment fields
- [ ] `order_payments_management/migrations/0005_discountusage_and_more.py` - OrderPayment fields
- [ ] `fines/migrations/0005_alter_finetypeconfig_fields.py` - Fine type config fields

#### ✅ Test Migrations in Staging
```bash
# In staging environment
docker-compose exec web python manage.py migrate --plan
docker-compose exec web python manage.py migrate --dry-run
docker-compose exec web python manage.py migrate
```

**Expected Output**: All migrations should apply without errors.

#### ✅ Verify Database Schema
```bash
# Check that all tables exist
docker-compose exec db psql -U postgres -d writing_system -c "\dt writer_management_tip"
docker-compose exec db psql -U postgres -d writing_system -c "\dt loyalty_management_redemption*"
```

**Expected**: All tables should exist with correct columns.

#### ✅ Rollback Plan
- [ ] Document rollback migrations
- [ ] Test rollback procedure in staging
- [ ] Backup database before deployment

**Rollback Commands**:
```bash
# Rollback to previous migration
docker-compose exec web python manage.py migrate writer_management 0001
docker-compose exec web python manage.py migrate loyalty_management 0002
# ... (rollback other apps as needed)
```

---

### 2. Database Backup

#### ✅ Create Full Backup
```bash
# Create database backup
docker-compose exec db pg_dump -U postgres writing_system > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup file exists and is not empty
ls -lh backup_*.sql
```

**Requirements**:
- [ ] Backup file created successfully
- [ ] Backup file size > 0
- [ ] Backup stored in secure location
- [ ] Backup retention policy documented

#### ✅ Test Backup Restoration
```bash
# Test restore in test environment
docker-compose exec db psql -U postgres -d test_db < backup_*.sql
```

**Expected**: Database should restore without errors.

---

### 3. Code Review & Testing

#### ✅ Backend Testing
- [ ] Tip Management endpoints tested
  - [ ] Dashboard endpoint
  - [ ] List tips endpoint
  - [ ] Analytics endpoint
  - [ ] Earnings endpoint
- [ ] Loyalty Redemption endpoints tested
  - [ ] List categories
  - [ ] List items
  - [ ] Create category/item
  - [ ] List requests
  - [ ] Analytics

**Test Scripts**:
```bash
# Run test scripts
docker-compose exec web python test_tip_management_endpoints.py
docker-compose exec web python test_loyalty_redemption.py
```

**Expected**: All tests should pass.

#### ✅ Performance Testing
- [ ] Dashboard endpoint response time < 2s
- [ ] List tips endpoint response time < 1s (with pagination)
- [ ] Analytics endpoint response time < 3s
- [ ] No N+1 queries detected

**Tools**: Django Debug Toolbar, Django Silk

#### ✅ Security Review
- [ ] Permissions enforced (IsAdmin, IsAuthenticated)
- [ ] Website filtering working correctly
- [ ] Input validation in place
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified

---

### 4. API Documentation

#### ✅ Documentation Updated
- [ ] `TIP_MANAGEMENT_API_DOCUMENTATION.md` created
- [ ] `TIP_MANAGEMENT_USER_GUIDE.md` created
- [ ] Swagger/OpenAPI schema updated (auto-generated)
- [ ] All endpoints documented
- [ ] Query parameters documented
- [ ] Response formats documented
- [ ] Error responses documented

**Verify**:
```bash
# Check Swagger UI
curl http://localhost:8000/api/v1/docs/swagger/
```

---

### 5. Configuration

#### ✅ Environment Variables
- [ ] Database connection strings verified
- [ ] Redis connection strings verified
- [ ] JWT secret keys configured
- [ ] All required environment variables set

#### ✅ Settings Review
- [ ] `SPECTACULAR_SETTINGS` configured
- [ ] `ALLOWED_HOSTS` configured
- [ ] `CORS_ALLOWED_ORIGINS` configured
- [ ] Database indexes configured

---

### 6. Dependencies

#### ✅ Requirements Updated
- [ ] `requirements.txt` updated (if needed)
- [ ] All dependencies installed
- [ ] No dependency conflicts

**Check**:
```bash
docker-compose exec web pip check
```

---

### 7. Staging Deployment

#### ✅ Deploy to Staging
```bash
# Pull latest code
git pull origin main

# Build and restart services
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

#### ✅ Test in Staging
- [ ] All endpoints accessible
- [ ] Authentication working
- [ ] Permissions enforced
- [ ] Data filtering working
- [ ] Performance acceptable
- [ ] No errors in logs

**Test Endpoints**:
```bash
# Test dashboard
curl -H "Authorization: Bearer <token>" \
  http://staging.example.com/api/v1/admin-management/tips/dashboard/

# Test list tips
curl -H "Authorization: Bearer <token>" \
  http://staging.example.com/api/v1/admin-management/tips/list_tips/
```

---

### 8. Breaking Changes Review

#### ✅ Verify No Breaking Changes
- [ ] Existing endpoints still work
- [ ] Response formats unchanged (for existing endpoints)
- [ ] Authentication unchanged
- [ ] Permissions unchanged
- [ ] Database schema changes are backward compatible

**Check**:
- Review migration files for destructive operations
- Test existing API endpoints
- Verify frontend compatibility

---

### 9. Monitoring & Logging

#### ✅ Monitoring Setup
- [ ] Error logging configured
- [ ] Performance monitoring configured
- [ ] Database query logging enabled (for debugging)
- [ ] Alert thresholds configured

#### ✅ Log Review
- [ ] Check for errors in staging logs
- [ ] Check for warnings
- [ ] Verify log rotation configured

---

## Deployment Steps

### 1. Pre-Deployment
```bash
# 1. Create backup
docker-compose exec db pg_dump -U postgres writing_system > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Pull latest code
git pull origin main

# 3. Verify changes
git log --oneline -10
```

### 2. Deployment
```bash
# 1. Build services
docker-compose build

# 2. Stop services (if needed)
docker-compose down

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# 6. Restart services
docker-compose restart web
```

### 3. Post-Deployment Verification
```bash
# 1. Check service status
docker-compose ps

# 2. Check logs
docker-compose logs web --tail=100

# 3. Test endpoints
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/admin-management/tips/dashboard/
```

---

## Post-Deployment Checklist

### 1. Service Health

#### ✅ Service Status
- [ ] All services running
- [ ] No service crashes
- [ ] Database connection working
- [ ] Redis connection working
- [ ] Celery workers running

**Check**:
```bash
docker-compose ps
docker-compose logs web --tail=50
docker-compose logs celery --tail=50
```

#### ✅ Endpoint Availability
- [ ] Dashboard endpoint accessible
- [ ] List tips endpoint accessible
- [ ] Analytics endpoint accessible
- [ ] Earnings endpoint accessible
- [ ] Loyalty redemption endpoints accessible

**Test**:
```bash
# Test each endpoint
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/admin-management/tips/dashboard/
```

---

### 2. Error Monitoring

#### ✅ Error Logs
- [ ] No critical errors in logs
- [ ] No authentication errors
- [ ] No permission errors
- [ ] No database errors
- [ ] No migration errors

**Check**:
```bash
# Check for errors
docker-compose logs web | grep -i error
docker-compose logs web | grep -i exception
```

#### ✅ Application Logs
- [ ] Review application logs
- [ ] Check for warnings
- [ ] Verify log rotation working

---

### 3. Performance Monitoring

#### ✅ Response Times
- [ ] Dashboard endpoint < 2s
- [ ] List tips endpoint < 1s
- [ ] Analytics endpoint < 3s
- [ ] Earnings endpoint < 2s

**Monitor**:
- Use Django Debug Toolbar
- Check application logs for slow queries
- Monitor database query times

#### ✅ Database Performance
- [ ] No slow queries detected
- [ ] Indexes being used
- [ ] No N+1 queries
- [ ] Query count acceptable

**Check**:
```bash
# Enable query logging
# Check Django Debug Toolbar
# Review database query logs
```

#### ✅ Resource Usage
- [ ] CPU usage normal
- [ ] Memory usage normal
- [ ] Database connections within limits
- [ ] Redis memory usage normal

---

### 4. Data Verification

#### ✅ Data Integrity
- [ ] Tips can be created
- [ ] Tips can be retrieved
- [ ] Tip calculations correct
- [ ] Writer earnings correct
- [ ] Platform profit correct

#### ✅ Database Integrity
- [ ] All tables exist
- [ ] All columns exist
- [ ] Foreign keys working
- [ ] Indexes created
- [ ] Constraints enforced

**Verify**:
```bash
# Check tables
docker-compose exec db psql -U postgres -d writing_system -c "\dt writer_management_tip"
docker-compose exec db psql -U postgres -d writing_system -c "\d writer_management_tip"
```

---

### 5. Permissions & Security

#### ✅ Permissions
- [ ] Admin users can access endpoints
- [ ] Non-admin users cannot access endpoints
- [ ] Website filtering working
- [ ] Superadmin can see all websites

**Test**:
- Login as admin and test endpoints
- Login as non-admin and verify access denied
- Test website filtering

#### ✅ Security
- [ ] Authentication required
- [ ] JWT tokens working
- [ ] Input validation working
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified

---

### 6. API Documentation

#### ✅ Swagger/OpenAPI
- [ ] Swagger UI accessible
- [ ] ReDoc accessible
- [ ] Schema generated correctly
- [ ] All endpoints documented
- [ ] Examples working

**Verify**:
```bash
# Check Swagger UI
curl http://localhost:8000/api/v1/docs/swagger/

# Check schema
curl http://localhost:8000/api/v1/schema/
```

---

### 7. Frontend Integration

#### ✅ Frontend Compatibility
- [ ] Frontend can access endpoints
- [ ] Response formats correct
- [ ] Error handling working
- [ ] Authentication working

**Note**: Frontend testing is pending and should be done separately.

---

### 8. Rollback Readiness

#### ✅ Rollback Plan
- [ ] Rollback procedure documented
- [ ] Database backup available
- [ ] Rollback migrations tested
- [ ] Rollback can be executed quickly

**Rollback Procedure**:
1. Stop services
2. Restore database backup
3. Rollback code to previous version
4. Restart services
5. Verify system working

---

## Monitoring Schedule

### First Hour
- [ ] Check logs every 15 minutes
- [ ] Monitor error rates
- [ ] Monitor response times
- [ ] Check service health

### First Day
- [ ] Review logs hourly
- [ ] Monitor performance metrics
- [ ] Check for user-reported issues
- [ ] Verify data integrity

### First Week
- [ ] Daily log review
- [ ] Performance analysis
- [ ] User feedback review
- [ ] Optimization opportunities

---

## Success Criteria

### ✅ Deployment Successful If:
1. All services running without errors
2. All endpoints accessible and working
3. No critical errors in logs
4. Performance within acceptable limits
5. Data integrity maintained
6. Permissions working correctly
7. Documentation accessible

### ❌ Rollback Required If:
1. Critical errors preventing functionality
2. Data corruption detected
3. Performance degradation > 50%
4. Security vulnerabilities discovered
5. Database migration failures

---

## Emergency Contacts

- **Development Team**: [Contact Info]
- **DevOps Team**: [Contact Info]
- **Database Administrator**: [Contact Info]

---

## Notes

- All checkboxes should be verified before deployment
- Keep deployment window short to minimize risk
- Have rollback plan ready
- Monitor closely after deployment
- Document any issues encountered

---

**Last Updated**: 2024-12-19  
**Version**: 1.0.0

