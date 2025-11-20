# Writing System Backend

A comprehensive Django REST API backend for a multi-tenant writing services platform. This system manages orders, payments, invoices, users, writers, clients, and administrative functions across multiple websites.

## 🎯 Overview

The Writing System Backend is a robust, scalable API platform that powers a writing services marketplace. It supports multiple websites (multi-tenant architecture), handles complex order workflows, payment processing, invoice management, and provides comprehensive dashboards for different user roles.

## ✨ Key Features

### Core Functionality
- **Multi-Tenant Architecture**: Support for multiple websites with isolated data
- **Order Management**: Complete order lifecycle from placement to completion
- **Payment Processing**: Integrated payment system with multiple payment methods
- **Invoice System**: Automated invoice generation and management
- **User Management**: Role-based access control (Superadmin, Admin, Writer, Client, Editor, Support)
- **Dashboard Analytics**: Real-time metrics and reporting for all user roles

### Advanced Features
- **Session Management**: Idle timeout with warning dialogs
- **Notification System**: Real-time notifications via SSE (Server-Sent Events)
- **Discount System**: Flexible discount codes and promotional campaigns
- **Loyalty Program**: Points-based loyalty and redemption system
- **Referral System**: User referral tracking and rewards
- **Fine Management**: Automated fine calculation and appeal system
- **Review System**: Order, writer, and website reviews
- **Class Management**: Bundle purchases and express classes
- **Special Orders**: Custom order workflows with installments
- **Wallet System**: Client and writer wallet management
- **Activity Logging**: Comprehensive audit trail
- **Blog & Service Pages**: CMS for content management
- **Support Tickets**: Integrated support ticket system

## 🛠️ Tech Stack

- **Framework**: Django 5.0.14
- **API**: Django REST Framework
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Task Queue**: Celery with Celery Beat
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **File Storage**: DigitalOcean Spaces (S3-compatible)
- **Email**: Gmail SMTP / SendGrid
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- Python 3.11+ (for local development without Docker)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd writing_system_backend
```

### 2. Environment Setup

```bash
# Copy environment template
cp env.template .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
```bash
SECRET_KEY=your-secret-key-here
POSTGRES_DB_NAME=writing_system_db
POSTGRES_USER_NAME=postgres
POSTGRES_PASSWORD=your-db-password
REDIS_PASSWORD=your-redis-password
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Start Services

```bash
# Start all services (web, db, redis, celery, beat)
docker-compose up -d

# Or start just the web server
docker-compose up -d web
```

### 4. Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### 5. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Verify Installation

```bash
# Check API root
curl http://localhost:8000/api/v1/

# Check service status
docker-compose ps
```

## 📁 Project Structure

```
writing_system_backend/
├── activity/                    # Activity logging system
├── admin_management/             # Admin dashboard and management
├── authentication/              # Authentication and session management
├── blog_pages_management/      # Blog content management
├── class_management/            # Class bundles and express classes
├── client_management/           # Client dashboard and features
├── client_wallet/               # Client wallet management
├── communications/              # Order communications
├── core/                        # Core utilities and shared code
├── discounts/                  # Discount and promotion system
├── editor_management/          # Editor management features
├── fines/                       # Fine calculation and appeals
├── loyalty_management/         # Loyalty points and rewards
├── mass_emails/                # Bulk email functionality
├── notifications_system/        # Notification system (SSE)
├── order_configs/              # Order configuration options
├── order_files/                 # Order file management
├── order_payments_management/   # Payment and invoice system
├── orders/                      # Order management
├── pricing_configs/            # Pricing configuration
├── referrals/                   # Referral system
├── refunds/                     # Refund processing
├── reviews_system/              # Review and rating system
├── service_pages_management/    # Service page CMS
├── special_orders/              # Special order workflows
├── support_management/          # Support ticket system
├── superadmin_management/       # Superadmin features
├── tickets/                     # Ticket system
├── users/                       # User management
├── wallet/                      # Wallet system
├── websites/                    # Multi-tenant website management
├── writer_management/          # Writer dashboard and features
├── writer_payments_management/  # Writer payment processing
└── writer_wallet/               # Writer wallet management
```

## 🔧 Development

### Running Locally (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Docker Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f web

# Run management commands
docker-compose exec web python manage.py <command>

# Access container shell
docker-compose exec web bash

# Restart service
docker-compose restart web
```

### Running Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test orders

# Run integration tests
./run_integration_tests.sh
```

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/v1/docs/swagger/
- **ReDoc**: http://localhost:8000/api/v1/docs/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/v1/schema/

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/refresh-token/` - Refresh JWT token
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/session-management/status/` - Session status

#### Orders
- `GET /api/v1/orders/` - List orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/{id}/` - Order details

#### Payments & Invoices
- `GET /api/v1/order-payments/` - List payments
- `GET /api/v1/order-payments/invoices/` - List invoices
- `POST /api/v1/order-payments/invoices/` - Create invoice

#### Dropdown Options
- `GET /api/v1/dropdown-options/` - Get all dropdown options
- `GET /api/v1/dropdown-options/{category}/` - Get specific category

See [DROPDOWN_OPTIONS_API.md](./DROPDOWN_OPTIONS_API.md) for details.

### Authentication

All API endpoints (except login/register) require JWT authentication:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/v1/orders/
```

## 🎨 Key Features Documentation

- **[Invoice System](./INVOICE_PAYMENT_SYSTEM_DESIGN.md)**: Complete invoice and payment workflow
- **[Session Management](./SESSION_MANAGEMENT_COMPLETE.md)**: Idle timeout and session tracking
- **[Dropdown Options API](./DROPDOWN_OPTIONS_API.md)**: Database-driven dropdown lists
- **[Performance Optimizations](./PERFORMANCE_IMPROVEMENTS_COMPLETED.md)**: Query optimizations and caching
- **[Multi-Domain Deployment](./MULTI_DOMAIN_DEPLOYMENT_GUIDE.md)**: Production deployment guide
- **[Docker Guide](./DOCKER_README.md)**: Detailed Docker setup and deployment

## 🚢 Deployment

### Production Deployment

```bash
# Using deployment script
./deploy.sh prod

# Or manually
docker-compose -f docker-compose.prod.yml up -d --build
```

### Environment Variables for Production

```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-production-secret-key
# ... other production settings
```

See [PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md) for complete deployment instructions.

## 🔐 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Session timeout with idle detection
- CORS configuration
- SQL injection protection (Django ORM)
- XSS protection
- CSRF protection
- Rate limiting (via Nginx in production)

## 📊 Monitoring & Logging

### Health Checks

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
docker-compose logs -f celery
```

### Activity Logging

All user actions are logged in the `activity` app for audit trails.

## 🧪 Testing

```bash
# Run unit tests
docker-compose exec web python manage.py test

# Run integration tests
./run_integration_tests.sh

# Run E2E tests
python test_e2e.py
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

## 📝 Management Commands

### Database

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Show migration status
docker-compose exec web python manage.py showmigrations
```

### Static Files

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Celery

```bash
# Check Celery status
docker-compose exec celery celery -A writing_system inspect ping

# View Celery logs
docker-compose logs -f celery
```

## 🐛 Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check logs
docker-compose logs web

# Restart service
docker-compose restart web
```

**Database connection errors:**
```bash
# Check database logs
docker-compose logs db

# Verify environment variables
docker-compose exec web env | grep POSTGRES
```

**Port already in use:**
```bash
# Find process using port
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

**Proxy errors (ECONNREFUSED):**
- Ensure backend is running: `docker-compose ps`
- Check if web service is up: `docker-compose up -d web`
- See [PROXY_ERROR_FIX.md](./PROXY_ERROR_FIX.md) for details

## 📖 Additional Documentation

- [Docker Setup Guide](./DOCKER_README.md)
- [API Documentation](./COMPLETE_API_DOCUMENTATION.md)
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)
- [Performance Assessment](./PERFORMANCE_ASSESSMENT.md)
- [Migration Guide](./MIGRATION_GUIDE.md)

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review relevant documentation files
3. Check service health: `docker-compose ps`
4. Verify environment variables

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with Django, DRF, and modern Python best practices.

---

**Happy Coding! 🚀**

