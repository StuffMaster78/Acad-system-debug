# Client Website

A separate, dedicated client-facing interface for testing and simulating the complete client journey.

## Overview

This is a self-contained client website that provides a clean, focused experience for clients to:
- View their dashboard with statistics and recent activity
- Create and manage orders
- Track order progress
- Make payments
- Communicate with writers
- Manage their profile

## Structure

```
client/
├── layouts/
│   └── ClientLayout.vue      # Main layout with header and navigation
└── views/
    ├── ClientHome.vue         # Dashboard/home page
    ├── ClientOrders.vue       # Order list view
    ├── ClientOrderCreate.vue  # Order creation form
    ├── ClientOrderDetail.vue  # Order detail view
    ├── ClientPayments.vue     # Payment history and management
    ├── ClientMessages.vue     # Messaging interface
    └── ClientProfile.vue     # Profile settings
```

## Routes

All client routes are prefixed with `/client`:

- `/client` - Dashboard/Home
- `/client/orders` - Order list
- `/client/orders/create` - Create new order
- `/client/orders/:id` - Order details
- `/client/payments` - Payment management
- `/client/messages` - Messages/Communications
- `/client/profile` - Profile settings
- `/client/loyalty` - Loyalty & Rewards
- `/client/referrals` - Referrals

## Features

### Dashboard
- Overview statistics (active orders, total spent, wallet balance, loyalty points)
- Quick actions (place order, view orders, payments)
- Recent orders list
- Payment reminders

### Order Management
- View all orders with filtering and search
- Create new orders with a simplified form
- View order details with status tracking
- Request revisions
- Cancel orders (when applicable)

### Payments
- View wallet balance
- View payment history
- Make payments for pending orders
- Add funds to wallet

### Messaging
- View all conversation threads
- Send and receive messages
- Real-time message updates
- Order-specific conversations

### Profile
- Update personal information
- View account statistics
- Manage contact preferences

## Usage

### For Testing

1. **Login as a client user**
   - Navigate to `/login` and use client credentials
   - After login, you'll be redirected to the main dashboard

2. **Access the client website**
   - Navigate to `/client` to access the dedicated client interface
   - Or use the client-specific routes directly

3. **Simulate client journey**
   - Create an order: `/client/orders/create`
   - View orders: `/client/orders`
   - Track order: `/client/orders/:id`
   - Make payment: `/client/payments`
   - Message writer: `/client/messages`

### For Development

The client website uses the same API endpoints as the main application but provides a simplified, client-focused UI. All components are located in `frontend/src/client/`.

## Design Principles

1. **Simplicity**: Clean, uncluttered interface focused on client needs
2. **Clarity**: Clear navigation and action buttons
3. **Responsiveness**: Works on all device sizes
4. **Consistency**: Uses the same design system as the main app
5. **Accessibility**: Follows accessibility best practices

## Integration

The client website:
- Uses the same authentication system (`useAuthStore`)
- Connects to the same API endpoints
- Shares common components from `@/components`
- Uses the same API clients from `@/api`

## Future Enhancements

- Order templates and presets
- Advanced filtering and search
- Order analytics and insights
- Payment methods integration
- Real-time notifications
- Mobile app support

## Notes

- The client website is separate from the main admin/writer interfaces
- It's designed specifically for client users (role: 'client')
- All routes require authentication and client role
- The layout is optimized for client workflows

