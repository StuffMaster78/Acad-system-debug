# Writing System Frontend

Vue.js 3 frontend application for the Writing System platform.

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API service files
│   │   ├── client.js     # Axios instance with interceptors
│   │   ├── auth.js       # Authentication API
│   │   └── admin/        # Admin API services
│   ├── stores/           # Pinia stores
│   │   └── auth.js       # Authentication store
│   ├── router/           # Vue Router
│   │   └── index.js     # Router configuration
│   ├── views/            # Page components
│   │   ├── auth/         # Authentication pages
│   │   ├── account/      # Account management
│   │   └── admin/        # Admin pages
│   ├── components/       # Reusable components
│   ├── utils/            # Utility functions
│   ├── App.vue          # Root component
│   └── main.js          # Application entry point
├── package.json
├── vite.config.js
└── .env                  # Environment variables
```

## Features

- ✅ JWT Authentication
- ✅ Password Management (Change/Reset)
- ✅ Magic Link Login
- ✅ 2FA Support
- ✅ Session Management
- ✅ Tip Management Dashboard
- ✅ Admin Features
- ✅ Responsive Design

## API Integration

The frontend connects to the backend API at `http://localhost:8000/api/v1`

All API calls are handled through the `apiClient` with automatic:
- Token injection
- Token refresh on expiration
- Error handling
- Request/response interceptors

## Environment Variables

See `.env` file for configuration:
- `VUE_APP_API_URL` - Backend API URL
- `VUE_APP_NAME` - Application name
- `VUE_APP_ENV` - Environment (development/production)

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

For detailed integration guides, see:
- `../frontend_integration/SETUP_INSTRUCTIONS.md`
- `../frontend_integration/FRONTEND_COMPONENTS_GUIDE.md`
- `../AUTH_SYSTEM_REVIEW_AND_IMPROVEMENTS.md`

