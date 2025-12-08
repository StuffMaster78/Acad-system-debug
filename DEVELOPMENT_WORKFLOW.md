# Development Workflow Guide

## 🎯 Overview

This guide outlines the development workflow for the Writing System Platform, including setup, coding standards, testing, and contribution guidelines.

## 🚀 Getting Started

### Prerequisites

- **Git**: Version control
- **Docker & Docker Compose**: Containerization
- **Node.js 18+**: Frontend development
- **Python 3.11+**: Backend development
- **IDE**: VS Code (recommended) or your preferred editor

### Initial Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd writing_project

# 2. Set up environment
cp .env.example .env  # Configure environment variables

# 3. Start services with Docker
docker-compose up -d

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Create superuser (optional)
docker-compose exec web python manage.py createsuperuser

# 6. Install frontend dependencies
cd frontend
npm install
```

## 🔄 Daily Workflow

### Starting Work

```bash
# 1. Update your local develop branch
git checkout develop
git pull origin develop

# 2. Create a new feature branch
git checkout -b feature/your-feature-name

# 3. Start Docker services (if not running)
docker-compose up -d

# 4. Start frontend dev server
cd frontend
npm run dev
```

### Making Changes

1. **Write Code**: Follow coding standards (see below)
2. **Test Locally**: Run tests before committing
3. **Commit Changes**: Use conventional commits
4. **Push & Create PR**: Push branch and create pull request

### Before Committing

```bash
# Backend checks
cd backend
python manage.py check
python manage.py test  # Run tests
black .  # Format code
isort .  # Sort imports
flake8 .  # Lint code

# Frontend checks
cd frontend
npm run lint  # Lint code
npm run format  # Format code
npm test  # Run tests
npm run build  # Verify build works
```

## 📝 Coding Standards

### Backend (Python/Django)

#### Code Style
- Follow **PEP 8** guidelines
- Use **Black** for formatting (line length: 127)
- Use **isort** for import sorting
- Maximum line length: 127 characters

#### Naming Conventions
- **Classes**: `PascalCase` (e.g., `OrderService`)
- **Functions/Methods**: `snake_case` (e.g., `process_order`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private**: Prefix with `_` (e.g., `_internal_method`)

#### Django Best Practices
- Use class-based views when appropriate
- Keep views thin, move logic to services
- Use serializers for data validation
- Use `select_related` and `prefetch_related` for queries
- Add database indexes for frequently queried fields

#### Example

```python
# ✅ Good
class OrderService:
    def process_order(self, order_id: int) -> Order:
        """Process an order and return the updated order."""
        order = Order.objects.select_related('client').get(id=order_id)
        # ... processing logic
        return order

# ❌ Bad
def processOrder(orderId):
    order = Order.objects.get(id=orderId)  # N+1 query issue
    # ... processing logic
```

### Frontend (Vue.js)

#### Code Style
- Follow **Vue.js Style Guide**
- Use **ESLint** for linting
- Use **Prettier** for formatting
- Use **Composition API** (`<script setup>`)

#### Naming Conventions
- **Components**: `PascalCase` (e.g., `OrderList.vue`)
- **Composables**: `camelCase` with `use` prefix (e.g., `useAuth.js`)
- **Utilities**: `camelCase` (e.g., `errorHandler.js`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)

#### Vue Best Practices
- Use Composition API
- Keep components focused and small
- Extract reusable logic to composables
- Use TypeScript-style JSDoc for complex functions
- Handle errors gracefully

#### Example

```vue
<!-- ✅ Good -->
<script setup>
import { ref, computed } from 'vue'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  }
})

const { error: showError } = useToast()
const loading = ref(false)

const order = computed(() => {
  // ... computed logic
})
</script>

<!-- ❌ Bad -->
<script>
export default {
  data() {
    return {
      orderId: null,
      loading: false
    }
  }
}
</script>
```

## 🧪 Testing

### Backend Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_orders.py

# Run tests by marker
pytest -m unit
pytest -m integration
```

### Frontend Testing

```bash
# Run all tests
cd frontend
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test  # Watch mode by default

# Run once
npm run test:run
```

### Test Coverage Requirements

- **Minimum**: 70% coverage
- **Critical paths**: 90%+ coverage
- **New code**: Must include tests

## 🔍 Code Review Process

### Before Submitting PR

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No console.log statements
- [ ] No hardcoded secrets
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] PR description is clear

### Review Checklist

- [ ] Code quality and style
- [ ] Test coverage
- [ ] Security considerations
- [ ] Performance implications
- [ ] Documentation completeness
- [ ] Breaking changes documented

## 📦 Commit Workflow

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Examples

```bash
# Feature
git commit -m "feat(orders): add order cancellation feature"

# Bug fix
git commit -m "fix(auth): resolve login timeout issue"

# Documentation
git commit -m "docs(api): update authentication endpoints"

# Refactoring
git commit -m "refactor(payments): simplify payment processing"
```

### Commit Best Practices

- ✅ Write clear, descriptive messages
- ✅ Use present tense ("add" not "added")
- ✅ Keep subject line under 50 characters
- ✅ Reference issues/tickets when applicable
- ❌ Don't commit commented-out code
- ❌ Don't commit large files
- ❌ Don't commit secrets/credentials

## 🚢 Pull Request Process

### Creating a PR

1. **Push your branch**
   ```bash
   git push origin feature/your-feature
   ```

2. **Create PR on GitHub**
   - Use the PR template
   - Fill in all relevant sections
   - Link related issues
   - Add screenshots if UI changes

3. **Wait for CI checks**
   - All checks must pass
   - Address any failures

4. **Request reviews**
   - Assign reviewers
   - Request review from team

5. **Address feedback**
   - Make requested changes
   - Push updates
   - Respond to comments

6. **Merge**
   - Squash and merge (recommended)
   - Delete branch after merge

### PR Title Format

Follow the same convention as commits:

```
feat(orders): add order cancellation feature
fix(auth): resolve login timeout issue
```

## 🐛 Debugging

### Backend Debugging

```bash
# Django shell
docker-compose exec web python manage.py shell

# View logs
docker-compose logs -f web

# Run with debugger
# Add breakpoint() in code
```

### Frontend Debugging

```bash
# Dev server with source maps
npm run dev

# Browser DevTools
# Use Vue DevTools extension
# Check Network tab for API calls
# Check Console for errors
```

## 🔧 Common Tasks

### Database Migrations

```bash
# Create migration
docker-compose exec web python manage.py makemigrations

# Apply migration
docker-compose exec web python manage.py migrate

# Rollback (if needed)
docker-compose exec web python manage.py migrate app_name previous_migration
```

### Updating Dependencies

```bash
# Backend
cd backend
pip install package-name
pip freeze > requirements.txt

# Frontend
cd frontend
npm install package-name
# package.json and package-lock.json updated automatically
```

### Resolving Merge Conflicts

```bash
# Update from develop
git checkout develop
git pull origin develop

# Merge into your branch
git checkout feature/your-feature
git merge develop

# Resolve conflicts
# Edit conflicted files
git add .
git commit -m "merge: resolve conflicts with develop"
```

## 📚 Resources

- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [Vue.js Style Guide](https://vuejs.org/style-guide/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)

## 🆘 Getting Help

- **Documentation**: Check project docs
- **Issues**: Create GitHub issue
- **Team**: Ask in team chat/email
- **Code Review**: Request help in PR comments

