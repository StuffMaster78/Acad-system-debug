# Contributing to Writing System Platform

We welcome contributions! This document provides guidelines and instructions for contributing to the Writing System Platform.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected vs. actual behavior
- Environment details (OS, Python version, Docker version, etc.)
- Relevant logs or error messages

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- A clear description of the feature
- Use cases and examples
- Potential implementation approach (if you have ideas)
- Any related issues or discussions

### Pull Requests

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards
   - Follow PEP 8 for Python code
   - Use ESLint for JavaScript/Vue code
   - Write clear, descriptive commit messages
   - Add tests for new features

3. **Test your changes**
   ```bash
   # Backend tests
   docker-compose exec web python manage.py test
   
   # Frontend tests (if configured)
   cd frontend && npm test
   ```

4. **Update documentation** if needed
   - Update README.md if adding new features
   - Add docstrings to new functions/classes
   - Update API documentation if changing endpoints

5. **Submit a pull request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all tests pass
   - Request review from maintainers

## 📋 Development Setup

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd writing_project
   ```

2. **Set up environment**
   ```bash
   cp backend/env.template backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser** (optional)
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## 🎨 Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **Black** for code formatting (if configured)
- Maximum line length: 100 characters
- Use type hints where appropriate
- Write docstrings for all functions and classes

Example:
```python
def process_order(order_id: int) -> dict:
    """
    Process an order and return the result.
    
    Args:
        order_id: The ID of the order to process
        
    Returns:
        Dictionary containing order status and details
    """
    # Implementation
    pass
```

### JavaScript/Vue (Frontend)

- Follow **ESLint** rules
- Use **Prettier** for formatting (if configured)
- Use Vue 3 Composition API
- Follow Vue.js style guide
- Use TypeScript where possible (if configured)

Example:
```javascript
// Use composition API
import { ref, computed } from 'vue'

export default {
  setup() {
    const count = ref(0)
    const doubleCount = computed(() => count.value * 2)
    
    return { count, doubleCount }
  }
}
```

### Git Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: Add refund management system
fix: Resolve session timeout issue
docs: Update API documentation
refactor: Optimize database queries
```

## 🧪 Testing

### Backend Tests

- Write unit tests for new features
- Write integration tests for API endpoints
- Aim for >80% code coverage
- Use Django's test framework

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test orders

# Run with coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

### Frontend Tests

- Write unit tests for components
- Write integration tests for complex features
- Use Vue Test Utils

```bash
# Run frontend tests (if configured)
cd frontend
npm test
```

## 📝 Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Document complex algorithms or business logic
- Include examples in docstrings where helpful

### API Documentation

- Update OpenAPI/Swagger documentation for new endpoints
- Include request/response examples
- Document authentication requirements
- Document error responses

### README Updates

- Update main README.md for major features
- Update backend/README.md for backend-specific changes
- Update frontend/README.md for frontend-specific changes
- Keep setup instructions current

## 🔍 Code Review Process

1. **Automated Checks**
   - All tests must pass
   - Code must pass linting
   - No merge conflicts

2. **Review Criteria**
   - Code follows style guidelines
   - Tests are included and passing
   - Documentation is updated
   - No security vulnerabilities
   - Performance considerations addressed

3. **Review Feedback**
   - Address all review comments
   - Make requested changes
   - Respond to questions
   - Update PR description if needed

## 🚀 Release Process

Releases are managed by maintainers. When your PR is merged:
- It will be included in the next release
- Release notes will be generated
- Version numbers will be updated

## 📞 Getting Help

- Check existing documentation
- Search existing issues
- Ask questions in discussions
- Contact maintainers for urgent issues

## 🙏 Thank You!

Thank you for contributing to the Writing System Platform! Your contributions help make this project better for everyone.

