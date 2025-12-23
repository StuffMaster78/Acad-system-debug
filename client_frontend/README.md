# Client Frontend - Public Website

A modern, public-facing website for the writing services platform, similar to EssayPro. This website allows clients to browse services, view pricing, place orders, and access content.

## 🎯 Features

- **Homepage** with hero section and service highlights
- **Order Wizard** - Step-by-step order creation with price calculator
- **Pricing Page** - Dynamic pricing calculator and pricing tiers
- **Services Page** - Overview of all available writing services
- **Blog** - Blog posts and content pages
- **Authentication** - Login and registration
- **Multi-Tenant Support** - Automatic website detection and branding
- **Responsive Design** - Mobile-friendly interface

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The development server will run on `http://localhost:5174`

## 📁 Project Structure

```
client_frontend/
├── src/
│   ├── api/              # API clients
│   │   ├── client.js      # Axios instance
│   │   ├── auth.js        # Authentication endpoints
│   │   └── services.js    # Service endpoints
│   ├── components/        # Reusable components
│   │   ├── Layout.vue
│   │   ├── Header.vue
│   │   └── Footer.vue
│   ├── stores/           # Pinia stores
│   │   ├── auth.js       # Authentication store
│   │   └── website.js    # Website/branding store
│   ├── views/            # Page components
│   │   ├── Home.vue
│   │   ├── OrderWizard.vue
│   │   ├── Pricing.vue
│   │   ├── Services.vue
│   │   ├── Blog.vue
│   │   ├── Dashboard.vue
│   │   ├── auth/
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   └── SeoPage.vue
│   ├── router/           # Vue Router configuration
│   ├── assets/           # CSS and static assets
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🔌 Backend Integration

### API Configuration

The frontend connects to the backend API. Configure the API base URL:

1. Create `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

2. Or use the default proxy configuration in `vite.config.js` (proxies `/api` to `http://localhost:8000`)

### Required Backend Endpoints

The frontend uses these backend endpoints:

- `GET /api/v1/websites/websites/` - Get website info
- `POST /api/v1/auth/auth/login/` - Login
- `POST /api/v1/auth/auth/register/` - Register
- `POST /api/v1/orders/orders/quote/` - Get price quote
- `POST /api/v1/orders/orders/create/` - Create order
- `GET /api/v1/blog_pages_management/blog-posts/` - List blog posts
- `GET /api/v1/blog_pages_management/blog-posts/{slug}/` - Get blog post
- `GET /api/v1/seo-pages/seo-pages/{slug}/` - Get SEO page

## 🎨 Multi-Tenant Branding

The website automatically detects the current domain and loads the corresponding website configuration from the backend:

- **Logo** - Displays website logo in header
- **Theme Color** - Applies website theme color
- **Site Name** - Uses website name throughout
- **Contact Info** - Shows website contact details in footer

## 📱 Pages

### Home (`/`)
- Hero section with CTA
- Features showcase
- Services preview
- Call-to-action sections

### Order Wizard (`/order`)
- Step 1: Order details (paper type, level, pages, deadline)
- Step 2: Instructions and file upload
- Step 3: Price review and order submission
- Supports guest checkout

### Pricing (`/pricing`)
- Interactive price calculator
- Pricing tiers display
- Direct order placement

### Services (`/services`)
- Overview of all writing services
- Service features and benefits
- Quick order links

### Blog (`/blog`)
- List of published blog posts
- Blog post detail pages
- SEO-friendly URLs

### Authentication
- **Login** (`/login`) - User login
- **Register** (`/register`) - New user registration

### Dashboard (`/dashboard`)
- Basic client dashboard
- Links to full dashboard (in main client portal)

## 🛠️ Technologies

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Next-generation frontend tooling
- **Vue Router** - Official router for Vue.js
- **Pinia** - State management
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client

## 🔒 Security

- JWT token-based authentication
- Secure token storage in localStorage
- Automatic token refresh
- Protected routes with navigation guards
- API request interceptors for error handling

## 📦 Deployment

### Build

```bash
npm run build
```

Output will be in the `dist/` directory.

### Environment Variables

For production, set:
```env
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
```

### Nginx Configuration

Example Nginx config for serving the built files:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    root /var/www/client_frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚧 Development Notes

- The website supports **guest checkout** - users can place orders without creating an account
- Multi-tenant detection happens automatically on page load
- All API calls include proper error handling
- Responsive design works on all screen sizes

## 📝 TODO

- [ ] Add order tracking page
- [ ] Implement payment integration
- [ ] Add live chat support
- [ ] Enhance SEO with meta tags
- [ ] Add analytics tracking
- [ ] Implement service page detail views
- [ ] Add testimonials section
- [ ] Create FAQ page

## 🤝 Contributing

This is part of the larger writing services platform. See the main project README for contribution guidelines.

## 📄 License

MIT

