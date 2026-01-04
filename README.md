# Writing System Platform

[![Backend Tests](https://github.com/awinooliyo/Order-Management-System/workflows/Comprehensive%20Test%20Suite/badge.svg)](https://github.com/awinooliyo/Order-Management-System/actions)
[![Frontend Tests](https://github.com/awinooliyo/Order-Management-System/workflows/Comprehensive%20Test%20Suite/badge.svg)](https://github.com/awinooliyo/Order-Management-System/actions)
[![Code Coverage](https://codecov.io/gh/awinooliyo/Order-Management-System/branch/main/graph/badge.svg)](https://codecov.io/gh/awinooliyo/Order-Management-System)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive multi-tenant writing services platform with Django REST API backend and Vue.js frontend. This system manages orders, payments, invoices, users, writers, clients, and administrative functions across multiple websites.

## 🎯 Overview

The Writing System Platform is a robust, scalable marketplace for writing services. It supports multiple websites (multi-tenant architecture), handles complex order workflows, payment processing, invoice management, and provides comprehensive dashboards for different user roles (Superadmin, Admin, Writer, Client, Editor, Support).

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
- **Rush Mode/Urgent Orders**: Urgent order placement with deadline normalization and higher earnings
- **Free Revision Eligibility**: Automatic tracking of revision windows with clear client messaging
- **File Type Configuration**: Categorized file management (Order instructions, Sample papers, Plagiarism reports, etc.)
- **Holiday & Special Days Management**: Admin management of holidays and promotional campaigns
- **Notification Profiles UI**: Enhanced data-table-centric notification management
- **Writer Profile Enhancements**: Auto-creation and default welcome messages
- **Admin Workload Override**: Admins can override writer level workload restrictions
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
- **Refund Management**: Complete refund request and processing workflow

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.0.14
- **API**: Django REST Framework
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Task Queue**: Celery with Celery Beat
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **File Storage**: DigitalOcean Spaces (S3-compatible)
- **Email**: Gmail SMTP / SendGrid

### Frontend
- **Framework**: Vue.js 3
- **Build Tool**: Vite
- **State Management**: Pinia
- **UI Framework**: Tailwind CSS
- **Charts**: ApexCharts
- **Rich Text**: Quill Editor
- **Form Validation**: VeeValidate + Yup

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx (production)

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- Python 3.11+ (for local development without Docker)
- Node.js 18+ (for local frontend development)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd writing_project

# Run the automated setup
make setup
```

This command will:
1. Copy environment templates
2. Start all Docker services
3. Run database migrations
4. Create a default superuser (`admin@writingsystem.com` / `password`)

### Option 2: Manual Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd writing_project
```

#### 2. Environment Setup

```bash
# Copy environment templates
cp backend/env.template backend/.env
cp frontend/.env.example frontend/.env  # if exists

# Edit backend/.env with your configuration
nano backend/.env
```

Required environment variables (see `.env.example` for full list):
```bash
SECRET_KEY=your-secret-key-here
POSTGRES_DB_NAME=writing_system_db
POSTGRES_USER_NAME=postgres
POSTGRES_PASSWORD=your-db-password
REDIS_PASSWORD=your-redis-password
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### 3. Start Services

```bash
# Start all services (web, db, redis, celery, beat)
docker-compose up -d

# Or start just the web server
docker-compose up -d web
```

#### 4. Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

#### 5. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

#### 6. Verify Installation

```bash
# Check API root
curl http://localhost:8000/api/v1/

# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
```

## 📂 Project Structure

```
writing_project/
├── backend/                    # Django REST API backend
│   ├── activity/              # Activity logging system
│   ├── admin_management/      # Admin dashboard and management
│   ├── authentication/        # Authentication and session management
│   ├── blog_pages_management/ # Blog content management
│   ├── class_management/      # Class bundles and express classes
│   ├── client_management/     # Client dashboard and features
│   ├── client_wallet/         # Client wallet management
│   ├── communications/        # Order communications
│   ├── core/                  # Core utilities and shared code
│   ├── discounts/            # Discount and promotion system
│   ├── editor_management/    # Editor management features
│   ├── fines/                 # Fine calculation and appeals
│   ├── loyalty_management/    # Loyalty points and rewards
│   ├── notifications_system/  # Notification system (SSE)
│   ├── orders/                # Order management
│   ├── order_payments_management/ # Payment and invoice system
│   ├── refunds/               # Refund processing
│   ├── reviews_system/        # Review and rating system
│   ├── support_management/    # Support ticket system
│   ├── users/                 # User management
│   ├── wallet/                # Wallet system
│   ├── websites/              # Multi-tenant website management
│   ├── writer_management/    # Writer dashboard and features
│   └── writing_system/        # Django project settings
├── frontend/                   # Vue.js SPA frontend
│   ├── src/
│   │   ├── api/               # API service files
│   │   ├── components/        # Reusable Vue components
│   │   ├── composables/       # Vue composables
│   │   ├── router/            # Vue Router configuration
│   │   ├── stores/            # Pinia stores
│   │   ├── utils/             # Utility functions
│   │   └── views/             # Page components
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml          # Development Docker Compose
├── docker-compose.prod.yml     # Production Docker Compose
├── Makefile                    # Development commands
└── README.md                   # This file
```

## 🛠️ Development Commands

The project uses a `Makefile` to streamline common development tasks.

| Command              | Description                                                         |
| -------------------- | ------------------------------------------------------------------- |
| `make setup`         | Runs the complete one-time setup for the dev environment.           |
| `make run`           | Starts the Django development server.                               |
| `make run-frontend`  | Starts the Vue.js development server.                               |
| `make run-celery`    | Starts the Celery worker for processing background tasks.           |
| `make run-celery-beat` | Starts the Celery beat scheduler for periodic tasks.                |
| `make test`          | Runs the full test suite.                                           |
| `make migrations`    | Creates new database migrations based on model changes.             |
| `make migrate`       | Applies pending database migrations.                                 |
| `make shell`         | Opens the Django shell.                                             |
| `make restart`       | Restarts the Docker environment and recreates the database.         |
| `make logs`          | Views logs from all services.                                       |

See the `Makefile` for all available commands.

## 📚 API Documentation

### Interactive Documentation

Once the backend is running, access the interactive API documentation:

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

### Authentication

All API endpoints (except login/register) require JWT authentication:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/v1/orders/
```

## 🎨 Key Features Documentation

- **[System Improvements Analysis](./SYSTEM_IMPROVEMENTS_ANALYSIS.md)**: Comprehensive analysis from all user perspectives
- **[Invoice System](./backend/INVOICE_PAYMENT_SYSTEM_DESIGN.md)**: Complete invoice and payment workflow
- **[Session Management](./backend/SESSION_MANAGEMENT_COMPLETE.md)**: Idle timeout and session tracking
- **[Email Templates](./backend/EMAIL_TEMPLATES.md)**: Email template system and customization
- **[Geolocation Analysis](./backend/GEOLOCATION_ANALYSIS.md)**: IP geolocation implementation and IP2Location LITE comparison
- **[Dropdown Options API](./backend/DROPDOWN_OPTIONS_API.md)**: Database-driven dropdown lists
- **[Performance Optimizations](./backend/PERFORMANCE_IMPROVEMENTS_COMPLETED.md)**: Query optimizations and caching
- **[Multi-Domain Deployment](./backend/MULTI_DOMAIN_DEPLOYMENT_GUIDE.md)**: Production deployment guide
- **[Docker Guide](./backend/DOCKER_README.md)**: Detailed Docker setup and deployment
- **[Frontend Developer Guide](./frontend/FRONTEND_DEVELOPER_GUIDE.md)**: Comprehensive frontend development guide

## 🚢 Deployment

### Production Deployment

```bash
# Using deployment script
cd backend
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

See [PRODUCTION_DEPLOYMENT_GUIDE.md](./backend/PRODUCTION_DEPLOYMENT_GUIDE.md) for complete deployment instructions.

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
cd backend
./run_integration_tests.sh

# Run frontend tests (if configured)
cd frontend
npm test
```

## 🤝 Contributing

We welcome contributions! Please read our **[CONTRIBUTING.md](./CONTRIBUTING.md)** to learn how you can get involved, from reporting bugs to submitting code.

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

**Frontend not connecting to backend:**
- Ensure backend is running: `docker-compose ps`
- Check API URL in frontend `.env` file
- Verify CORS settings in backend

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Backend tests only
make test-backend
# or
cd backend && pytest

# Frontend tests only
make test-frontend
# or
cd frontend && npm run test

# With coverage
make coverage
```

### Test Coverage

- **Backend**: Minimum 95% coverage required
- **Frontend**: Minimum 80% coverage required

Coverage reports are generated in:
- Backend: `backend/htmlcov/index.html`
- Frontend: `frontend/coverage/index.html`

### CI/CD

Tests run automatically on:
- Every push to main/develop branches
- Pull requests
- Daily schedule (2 AM UTC)
- Manual trigger

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for comprehensive testing documentation.

## 📖 Additional Documentation

- [Backend README](./backend/README.md) - Detailed backend documentation
- [Frontend README](./frontend/README.md) - Detailed frontend documentation
- [Testing Guide](./TESTING_GUIDE.md) - Comprehensive testing documentation
- [Docker Setup Guide](./backend/DOCKER_README.md)
- [API Documentation](./backend/COMPLETE_API_DOCUMENTATION.md)
- [Deployment Checklist](./backend/DEPLOYMENT_CHECKLIST.md)
- [Performance Assessment](./backend/PERFORMANCE_ASSESSMENT.md)
- [Migration Guide](./backend/MIGRATION_GUIDE.md)

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review relevant documentation files
3. Check service health: `docker-compose ps`
4. Verify environment variables

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Copyright (c) 2025 Erick Awino**

For questions or inquiries, contact: rickawino@gmail.com

## 🙏 Acknowledgments

Built with Django, DRF, Vue.js, and modern web development best practices.

---

**Happy Coding! 🚀**
