# Developer Guide

**Version**: 1.1  
**Last Updated**: June 2026

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Setup](#development-setup)
4. [Architecture Overview](#architecture-overview)
5. [Coding Standards](#coding-standards)
6. [API Development](#api-development)
7. [Frontend Contract Notes](#frontend-contract-notes)
8. [Testing](#testing)
9. [Deployment](#deployment)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis (optional, for caching)
- Docker & Docker Compose (recommended)

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd writing_project
   ```

2. **Start with Docker**
   ```bash
   docker compose up -d
   ```

3. **Seed development data** (first time only)
   ```bash
   make seed
   # Equivalent to:
   #   seed_dev_data
   #   seed_pricing_defaults localhost
   #   seed_special_orders --with-orders
   #   seed_orders
   #   backfill_compensation_events
   #   seed_profiles        ← creates WriterProfile + ClientProfile for all demo users
   ```

4. **Or Setup Manually**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_dev_data
   python manage.py seed_profiles
   python manage.py runserver

   # Frontend
   cd frontend && pnpm install && pnpm dev
   ```

---

## 📁 Project Structure

```
writing_project/
├── backend/                 # Django backend
│   ├── apps/               # Django apps
│   │   ├── orders/        # Order management
│   │   ├── users/         # User management
│   │   ├── client_management/
│   │   ├── writer_management/
│   │   └── ...
│   ├── core/              # Core utilities
│   ├── writing_system/    # Main settings
│   └── manage.py
└── docs/                  # Documentation
```

---

## 🛠️ Development Setup

### Backend Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

There is no active frontend package in this repository. The next frontend will
be created from scratch in a separate package or repository and should consume
the backend through the OpenAPI contract.

---

## 🏗️ Architecture Overview

### Backend Architecture

- **Framework**: Django 4.x with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Style**: RESTful API
- **Documentation**: drf-spectacular (OpenAPI/Swagger)

### Frontend Boundary

The old frontend has been removed. Backend development should focus on stable
API contracts, serializers, permissions, schema annotations, and domain
services. Do not add frontend application code to this repository.

### Key Design Patterns

- **MVC** - Model-View-Controller (Django)
- **Repository Pattern** - API service layer
- **Observer Pattern** - Event handling

---

## Key Architecture Notes

### User services (`backend/users/services/`)

All user-domain services live in `users/services/`. The `services_legacy/` subdirectory contains **compatibility shims only** — each file is a one-liner re-export. Do not add new logic to `services_legacy/`; put it in `users/services/` directly.

### Order service families

Orders support four `service_family` values: `paper_order`, `design_order`, `diagram_order`, `combo_order`. The `unit_type` field reflects the quantum of work:

| family | unit_type | Key fields |
|---|---|---|
| `paper_order` | `page` | `base_quantity` = pages, `paper_type` required |
| `design_order` | `slide` or `design_concept` | `base_quantity` = slides or designs |
| `diagram_order` | `diagram` | `base_quantity` = diagrams |
| `combo_order` | `page` | paper fields + `total_price_override` for combined total |

### Order file URLs

All order file endpoints sit under `/api/v1/orders/orders/<id>/files/` — note the double `orders/` (the router prefix + the `orders/` mount in `order_file_urls`). Examples:

- `GET  /api/v1/orders/orders/{id}/files/`
- `POST /api/v1/orders/orders/{id}/files/instructions/`
- `POST /api/v1/orders/orders/{id}/files/style-references/`

### Lifecycle permissions

`CanViewOrderLifecycle` is intentionally permissive at `has_permission` (any authenticated user passes) — client ownership and writer assignment are verified in `has_object_permission`. Do not add `require_tenant = True` back to this permission class.

### Payment reminder models

`PaymentReminderConfig`, `PaymentReminderDeletionMessage`, `PaymentReminderSettings`, and `PaymentReminderSent` live in `orders/models/legacy_models/unpaid_order_payment_reminders.py` and are managed via `/api/v1/admin-management/payment-reminders/`.

---

## 📝 Coding Standards

### Python (Backend)

- **Style Guide**: PEP 8
- **Linter**: flake8, black
- **Type Hints**: Use type hints where possible
- **Docstrings**: Google style docstrings

```python
def get_order_details(order_id: int) -> dict:
    """
    Get detailed information about an order.
    
    Args:
        order_id: The ID of the order to retrieve.
        
    Returns:
        Dictionary containing order details.
        
    Raises:
        Order.DoesNotExist: If order doesn't exist.
    """
    order = Order.objects.get(id=order_id)
    return serialize_order(order)
```

## 🔌 API Development

### Creating New Endpoints

1. **Create ViewSet**
   ```python
   # backend/orders/views.py
   from rest_framework import viewsets
   from rest_framework.decorators import action
   
   class OrderViewSet(viewsets.ModelViewSet):
       queryset = Order.objects.all()
       serializer_class = OrderSerializer
       
       @action(detail=True, methods=['post'])
       def custom_action(self, request, pk=None):
           order = self.get_object()
           # Your logic here
           return Response({'status': 'success'})
   ```

2. **Register URL**
   ```python
   # backend/orders/urls.py
   from rest_framework.routers import DefaultRouter
   from .views import OrderViewSet
   
   router = DefaultRouter()
   router.register(r'orders', OrderViewSet)
   ```

3. **Add to Main URLs**
   ```python
   # backend/writing_system/urls.py
   path('api/v1/orders/', include('orders.urls')),
   ```

### API Best Practices

- Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- Return consistent response formats
- Handle errors gracefully
- Document endpoints with docstrings
- Add pagination for list endpoints
- Implement filtering and sorting

---

## Frontend Contract Notes

The upcoming frontend should be designed as a separate app that depends on
backend contracts, not backend internals.

Before frontend implementation begins:

- Generate and review the OpenAPI schema.
- Reduce drf-spectacular warnings that would make generated clients unreliable.
- Keep `backend/API_CONTRACT_FRONTEND.md` updated with temporary contract notes.
- Prefer canonical endpoints over dashboard-specific duplicates.
- Mark deprecated endpoints before the new frontend adopts them.

---

## 🧪 Testing

### Backend Testing

```python
# backend/orders/tests.py
from django.test import TestCase
from rest_framework.test import APIClient

class OrderTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Setup test data
    
    def test_create_order(self):
        response = self.client.post('/api/v1/orders/', {
            'topic': 'Test Order',
            # ... other fields
        })
        self.assertEqual(response.status_code, 201)
```

### Running Tests

```bash
# Backend health and release smokes
docker compose exec web python manage.py check
docker compose exec web python scripts/smoke_config_routes.py
docker compose exec web python scripts/smoke_role_journeys.py
docker compose exec web python scripts/smoke_wallet_admin.py

# Fuller backend test suite
docker compose exec web pytest tests/ -q

# Frontend
cd frontend && npm run typecheck
cd frontend && npm run test
cd frontend && npm run build
```

Run the smoke scripts after changes to config hub, class management, special orders, CMS intelligence routes, notifications, activity, or wallets. They intentionally exercise cross-role contracts so regressions like writer financial leaks, missing `available_actions`, broken config route names, and admin wallet adjustment failures are caught before manual QA.

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Setup database (PostgreSQL)
- [ ] Configure static files
- [ ] Setup media files storage
- [ ] Configure email backend
- [ ] Setup SSL/HTTPS
- [ ] Configure CORS
- [ ] Setup monitoring
- [ ] Configure backups

### Environment Variables

```bash
# Backend
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=yourdomain.com

# Frontend variables belong in the future frontend package, not this backend repo.
```

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

**Last Updated**: June 2026
