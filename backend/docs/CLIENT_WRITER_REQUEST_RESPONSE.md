# Client Writer Request Response Implementation

## Summary

Added support for clients to accept/pay, reject, or counter offer on writer requests for additional pages/slides.

## Backend Changes

### 1. Model Updates
**File**: `backend/orders/models.py`

**Added Fields to WriterRequest**:
- `client_counter_pages`: Client's counter offer for additional pages
- `client_counter_slides`: Client's counter offer for additional slides
- `client_counter_cost`: Client's counter offer cost
- `client_counter_reason`: Client's reason for counter offer
- `has_counter_offer`: Boolean flag indicating if client made a counter offer

### 2. Service Updates
**File**: `backend/orders/services/writer_request_service.py`

**Updated `client_respond()` method**:
- Now accepts `counter_offer_data` parameter
- Handles three response types:
  - **Accept**: Sets `client_approval = True`, status = `ACCEPTED`
  - **Reject**: Sets status = `DECLINED`
  - **Counter Offer**: Sets `has_counter_offer = True`, stores counter offer data, status remains `PENDING` for writer to respond

### 3. Action Updates
**File**: `backend/orders/actions/writer_requests_actions.py`

**Updated `ClientRespondToWriterRequestAction`**:
- Now accepts `response` parameter: 'approve', 'reject', or 'counter'
- Accepts `counter_offer` dict for counter offers
- Properly passes counter offer data to service

### 4. Serializer Updates
**File**: `backend/orders/serializers_legacy.py`

**Updated `WriterRequestSerializer`**:
- Added counter offer fields to serializer
- Fixed field names (estimated_cost, final_cost)

## Frontend Changes

### 1. Client Response Modal
**File**: `frontend/src/components/client/WriterRequestResponseModal.vue`

**Features**:
- Three response options:
  - **Accept & Pay**: Accepts request and processes payment
  - **Counter Offer**: Allows client to propose different amount/quantity
  - **Reject**: Declines request with reason

**Counter Offer Fields**:
- Counter pages/slides (based on request type)
- Counter cost (optional)
- Counter reason (required)

**Validation**:
- Reject requires reason
- Counter offer requires counter value and reason
- Accept requires no additional fields

### 2. API Updates
**File**: `frontend/src/api/orders.js`

**Added**:
- `clientRespondToWriterRequest(orderId, requestId, data)` endpoint

## Workflow

### Client Response Flow

1. **Writer submits request** → Status: `PENDING`
2. **Client views request** → Sees request details and estimated cost
3. **Client responds**:
   - **Accept**: Request approved, payment processed (if required), changes applied
   - **Counter Offer**: Status remains `PENDING`, writer can accept/reject counter
   - **Reject**: Status = `DECLINED`, request closed

### Counter Offer Flow

1. Client makes counter offer → `has_counter_offer = True`, status = `PENDING`
2. Writer receives notification of counter offer
3. Writer can:
   - Accept counter offer
   - Reject counter offer
   - Make another counter offer (future enhancement)

## API Usage

### Accept Request
```javascript
await ordersApi.clientRespondToWriterRequest(orderId, requestId, {
  response: 'approve'
})
```

### Reject Request
```javascript
await ordersApi.clientRespondToWriterRequest(orderId, requestId, {
  response: 'reject',
  reason: 'Not within budget'
})
```

### Counter Offer
```javascript
await ordersApi.clientRespondToWriterRequest(orderId, requestId, {
  response: 'counter',
  counter_offer: {
    counter_pages: 2,  // If page request
    counter_slides: 5,  // If slide request
    counter_cost: 50.00,  // Optional
    counter_reason: 'Can only afford 2 additional pages'
  }
})
```

## Migration Required

A migration is needed to add the counter offer fields to the `WriterRequest` model:

```python
python manage.py makemigrations orders --name add_writer_request_counter_offer_fields
python manage.py migrate
```

## Next Steps

1. **Writer Counter Offer Response**: Allow writers to respond to client counter offers
2. **Payment Processing**: Integrate payment processing for accepted requests
3. **Notifications**: Send notifications when counter offers are made
4. **Order Detail Integration**: Add component to OrderDetail view for clients
