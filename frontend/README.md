# Writing System Frontend

Vue.js 3 frontend application for the Writing System platform. A modern, responsive SPA built with Vue 3, Vite, Pinia, and Tailwind CSS.

## 🎯 Overview

The Writing System Frontend is a comprehensive single-page application that provides role-based dashboards and interfaces for Writers, Clients, Admins, Editors, and Support staff. It features real-time updates, session management, and a modern, responsive design.

## ✨ Key Features

- **JWT Authentication**: Secure token-based authentication with automatic refresh
- **Role-Based Dashboards**: Customized interfaces for each user role
- **Session Management**: Idle timeout with warning dialogs
- **Real-Time Updates**: SSE (Server-Sent Events) for notifications
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Rich Text Editing**: Quill editor for content creation
- **Form Validation**: VeeValidate with Yup schemas
- **State Management**: Pinia for centralized state
- **Charts & Analytics**: ApexCharts for data visualization

## 🛠️ Tech Stack

- **Framework**: Vue.js 3 (Composition API)
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **UI Framework**: Tailwind CSS
- **Charts**: ApexCharts
- **Rich Text**: Quill Editor
- **Form Validation**: VeeValidate + Yup
- **HTTP Client**: Axios
- **Icons**: Heroicons

## 📋 Prerequisites

- Node.js 18+
- npm or pnpm
- Backend API running (see [Backend README](../backend/README.md))

## 🚀 Quick Start

### Option 1: Using Makefile (Recommended)

From the project root:

```bash
make run-frontend
```

### Option 2: Manual Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
# or
pnpm install
```

#### 2. Environment Setup

Create a `.env` file (if not exists):

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_FULL_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Writing System
```

#### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port shown in terminal).

#### 4. Build for Production

```bash
# Build for all domains
npm run build:all

# Or build for specific domain
npm run build:writers
npm run build:clients
npm run build:staff
```

The built files will be in the `dist/` directory.

## 📁 Project Structure

The codebase is organized with a clear separation of concerns, following Vue.js best practices.

```
frontend/
├── src/
│   ├── api/                    # API service files
│   │   ├── client.js           # Axios instance with interceptors
│   │   ├── auth.js             # Authentication API
│   │   └── admin/              # Admin API services
│   ├── components/             # Reusable Vue components
│   │   ├── common/             # Common UI components
│   │   ├── dashboard/          # Dashboard-specific components
│   │   ├── orders/             # Order-related components
│   │   ├── payments/           # Payment components
│   │   └── ...                 # Other feature components
│   ├── composables/            # Vue composables (reusable logic)
│   │   ├── useAuth.js          # Authentication composable
│   │   ├── useToast.js         # Toast notifications
│   │   └── ...                 # Other composables
│   ├── router/                 # Vue Router configuration
│   │   └── index.js            # Route definitions
│   ├── stores/                 # Pinia stores
│   │   └── auth.js             # Authentication store
│   ├── utils/                  # Utility functions
│   │   ├── errorHandler.js     # Error handling utilities
│   │   ├── permissions.js      # Permission checking
│   │   └── ...                 # Other utilities
│   ├── views/                  # Page components (routes)
│   │   ├── auth/               # Authentication pages
│   │   ├── account/            # Account management
│   │   ├── admin/              # Admin pages
│   │   └── ...                 # Other views
│   ├── layouts/                # Layout components
│   │   └── DashboardLayout.vue # Main dashboard layout
│   ├── config/                 # Configuration files
│   │   └── adminNavigation.js   # Admin navigation config
│   ├── services/               # Service layer
│   │   └── sessionManager.js   # Session management
│   ├── styles/                 # Global styles
│   │   └── dashboard.css        # Dashboard-specific styles
│   ├── App.vue                 # Root component
│   └── main.js                 # Application entry point
├── package.json                # Dependencies and scripts
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
└── .env                        # Environment variables
```

## 🛠️ Development Commands

| Command              | Description                                                         |
| -------------------- | ------------------------------------------------------------------- |
| `npm run dev`        | Starts the Vite development server.                                  |
| `npm run build`      | Builds the application for production.                               |
| `npm run build:all`  | Builds for all domains (writers, clients, staff).                    |
| `npm run lint`       | Runs ESLint to check code quality.                                  |
| `npm run preview`    | Preview the production build locally.                                |

## API Integration

The frontend connects to the backend API at `http://localhost:8000/api/v1`

All API calls are handled through the `apiClient` with automatic:
- Token injection
- Token refresh on expiration
- Error handling
- Request/response interceptors

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_FULL_URL=http://localhost:8000/api/v1

# Application
VITE_APP_NAME=Writing System
VITE_APP_ENV=development
```

**Note**: In Vite, environment variables must be prefixed with `VITE_` to be exposed to the client.

## Development

### Running the Frontend

```bash
npm run dev
```

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Integration with Backend

The frontend is configured to proxy API requests to the backend:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## Authentication Flow

1. User logs in via `/login`
2. JWT tokens are stored in localStorage
3. Tokens are automatically included in API requests
4. Tokens are refreshed automatically on expiration
5. User is redirected to login if tokens are invalid

## Routes

- `/login` - Login page
- `/forgot-password` - Password reset
- `/dashboard` - User dashboard
- `/account/settings` - Account settings
- `/account/password-change` - Change password
- `/admin/tips` - Tip Management (Admin only)

## Documentation

### For Frontend Developers

- **[FRONTEND_DEVELOPER_GUIDE.md](./FRONTEND_DEVELOPER_GUIDE.md)** - Comprehensive guide covering:
  - Project structure and setup
  - Core concepts and patterns
  - API integration
  - Component development
  - State management
  - Routing and styling
  - Best practices

- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Quick reference for common patterns and code snippets

### Additional Resources

- `../frontend_integration/SETUP_INSTRUCTIONS.md` - Setup instructions
- `../frontend_integration/FRONTEND_COMPONENTS_GUIDE.md` - Component guide
- `../AUTH_SYSTEM_REVIEW_AND_IMPROVEMENTS.md` - Auth system documentation

