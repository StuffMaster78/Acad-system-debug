# Developer Guide

**Version**: 1.0  
**Last Updated**: December 2025

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Setup](#development-setup)
4. [Architecture Overview](#architecture-overview)
5. [Coding Standards](#coding-standards)
6. [API Development](#api-development)
7. [Frontend Development](#frontend-development)
8. [Testing](#testing)
9. [Deployment](#deployment)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
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
   docker-compose up -d
   ```

3. **Or Setup Manually**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver

   # Frontend
   cd frontend
   npm install
   npm run dev
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
├── frontend/              # Vue.js frontend
│   ├── src/
│   │   ├── api/          # API client methods
│   │   ├── components/    # Vue components
│   │   ├── views/         # Page views
│   │   ├── router/        # Vue Router
│   │   └── stores/        # Pinia stores
│   └── package.json
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

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

---

## 🏗️ Architecture Overview

### Backend Architecture

- **Framework**: Django 4.x with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Style**: RESTful API
- **Documentation**: drf-spectacular (OpenAPI/Swagger)

### Frontend Architecture

- **Framework**: Vue.js 3 with Composition API
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS

### Key Design Patterns

- **MVC** - Model-View-Controller (Django)
- **Component-Based** - Vue components
- **Repository Pattern** - API service layer
- **Observer Pattern** - Event handling

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

### JavaScript (Frontend)

- **Style Guide**: ESLint with Vue plugin
- **Formatter**: Prettier
- **Naming**: camelCase for variables, PascalCase for components

```javascript
// Component
export default {
  name: 'OrderCard',
  props: {
    orderId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const order = ref(null)
    
    const fetchOrder = async () => {
      order.value = await ordersAPI.getOrder(props.orderId)
    }
    
    return { order, fetchOrder }
  }
}
```

---

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

## 🎨 Frontend Development

### Creating Components

1. **Component Structure**
   ```vue
   <template>
     <div class="component-name">
       <!-- Template content -->
     </div>
   </template>
   
   <script setup>
   import { ref, computed } from 'vue'
   
   const props = defineProps({
     // Props definition
   })
   
   const emit = defineEmits(['event-name'])
   
   // Component logic
   </script>
   
   <style scoped>
   /* Component styles */
   </style>
   ```

2. **Using API Methods**
   ```javascript
   import ordersAPI from '@/api/orders'
   
   const orders = ref([])
   
   const fetchOrders = async () => {
     try {
       const response = await ordersAPI.getOrders()
       orders.value = response.data.results
     } catch (error) {
       console.error('Failed to fetch orders:', error)
     }
   }
   ```

### Component Best Practices

- Use Composition API
- Keep components focused and reusable
- Use props for data input
- Use emits for events
- Handle loading and error states
- Make components accessible

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

### Frontend Testing

```javascript
// frontend/src/components/__tests__/OrderCard.spec.js
import { mount } from '@vue/test-utils'
import OrderCard from '@/components/OrderCard.vue'

describe('OrderCard', () => {
  it('renders order information', () => {
    const wrapper = mount(OrderCard, {
      props: {
        orderId: 1
      }
    })
    expect(wrapper.text()).toContain('Order')
  })
})
```

### Running Tests

```bash
# Backend
python manage.py test

# Frontend
npm run test
```

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

# Frontend
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js Documentation](https://vuejs.org/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**Last Updated**: December 2025

