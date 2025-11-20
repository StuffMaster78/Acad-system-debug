# System Dry Run Test Instructions

## Overview
This comprehensive dry run test validates the complete system flow:
1. Setup test environment (users, website, configs)
2. Place an order
3. Simulate payment
4. Test communication (messages, threads)
5. Test order workflow (assignment, submission, completion)
6. Test additional features (notifications, tips, etc.)

## Running the Dry Run Test

### Option 1: Via Docker (Recommended)
```bash
docker-compose exec web python3 dry_run_system_test.py
```

### Option 2: Direct Python (if dependencies installed)
```bash
python3 dry_run_system_test.py
```

### Option 3: Via Django Shell
```bash
docker-compose exec web python3 manage.py shell
# Then copy-paste the script content
```

## What the Test Does

### 1. Environment Setup
- Creates or uses existing test website
- Creates test users:
  - Client: `dryrun_client@test.com` (password: `TestPassword123!`)
  - Writer: `dryrun_writer@test.com` (password: `TestPassword123!`)
  - Admin: `dryrun_admin@test.com` (password: `TestPassword123!`)
- Sets up order configurations (paper types, academic levels)
- Creates client wallet with $1000 balance

### 2. Order Placement
- Creates a test order with:
  - Topic: "Test Order - System Dry Run"
  - 5 pages
  - 7-day deadline
  - Standard essay type
- Uses `CreateOrderService` to ensure proper order creation
- Validates order status and pricing

### 3. Payment Processing
- Creates payment record using `OrderPaymentService`
- Processes wallet payment
- Validates payment status and order payment status
- Checks wallet balance after payment

### 4. Communication Testing
- Creates communication thread for the order
- Sends message from client to writer
- Sends reply from writer to client
- Validates message visibility and thread participation

### 5. Order Workflow
- Assigns writer to order
- Submits order (writer completes work)
- Completes order (admin approves)
- Validates status transitions

### 6. Additional Features
- Checks notifications created during the flow
- Tests tip creation (if order completed)
- Tests location detection (if available)

## Expected Output

The script will output:
- ✅ Green checkmarks for successful operations
- ❌ Red X marks for failures
- ℹ️ Yellow info messages for informational content
- → Cyan arrows for step-by-step progress
- 🎉 Success message if all tests pass

## Test Results

At the end, you'll see:
- **Passed Tests**: List of successful operations
- **Failed Tests**: List of failed operations (if any)
- **Warnings**: Non-critical issues
- **Created Objects**: IDs of created orders, payments, threads, messages
- **Test User Credentials**: Login info for frontend testing

## Troubleshooting

### Database Connection Issues
- Ensure Docker containers are running: `docker-compose up -d`
- Check database is accessible: `docker-compose exec db psql -U awinorick -d writingsondo`

### Missing Dependencies
- Run inside Docker container where all dependencies are installed
- Or install dependencies locally: `pip install -r requirements.txt`

### Permission Errors
- Ensure test users have proper roles and permissions
- Check website assignment for users

### Order Creation Fails
- Verify order configurations exist (paper types, academic levels)
- Check website is active
- Ensure client has proper role

### Payment Processing Fails
- Verify client wallet exists and has sufficient balance
- Check payment service is properly configured
- Ensure order has valid total_price

## Using Test Users in Frontend

After running the dry run, you can use these credentials to test the frontend:

- **Client**: `dryrun_client@test.com` / `TestPassword123!`
- **Writer**: `dryrun_writer@test.com` / `TestPassword123!`
- **Admin**: `dryrun_admin@test.com` / `TestPassword123!`

These users will have:
- Test order created
- Payment processed
- Communication thread active
- Order in various workflow states

## Cleanup (Optional)

To clean up test data after testing:
```python
# In Django shell
from django.contrib.auth import get_user_model
from orders.models import Order
from communications.models import CommunicationThread

User = get_user_model()

# Delete test users
User.objects.filter(email__startswith='dryrun_').delete()

# Or delete specific test order
Order.objects.filter(topic__contains='System Dry Run').delete()
```

## Next Steps

After successful dry run:
1. Test frontend with created test users
2. Verify order appears in admin dashboard
3. Test communication features in frontend
4. Test payment flow in frontend
5. Test order workflow transitions in frontend

