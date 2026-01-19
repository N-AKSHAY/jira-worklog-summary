# Contributing to Jira Worklog Summary

Thank you for your interest in contributing to this project. This document provides guidelines and instructions for contributing.

## Code of Conduct

This project is for internal use by Stabilix Solutions employees only. All contributors are expected to maintain professional standards and respect confidentiality.

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with required configuration (see README.md)
6. Run the application: `python app/main.py`

## Architecture Guidelines

This project follows **Hexagonal Architecture (Ports & Adapters)**:

- **Presentation Layer**: HTTP routes and controllers
- **Domain Layer**: Business logic and interfaces
- **Infrastructure Layer**: External service adapters
- **Core**: Shared utilities and cross-cutting concerns

### Key Principles

- **No direct DB calls from controllers**: Use repository pattern
- **Idempotent APIs**: All endpoints must be idempotent
- **Structured logging**: Use JSON logging format
- **Error handling**: All APIs must have proper error handling
- **Type hints**: Use TypeScript for frontend, type hints for Python

## Code Style

- Follow PEP 8 for Python code
- Use type hints where applicable
- Write clean, readable, production-ready code
- Prefer simplicity over cleverness
- Use fewer comments (code should be self-documenting)

## Testing

- Write tests for new features
- Ensure all tests pass before submitting
- Test error cases and edge cases

## Commit Messages

Use clear, descriptive commit messages:
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Be specific about what changed
- Reference issue numbers if applicable

Example:
```
Add table view toggle for worklogs
Fix logout button icon styling
Update README with OAuth setup instructions
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following the architecture guidelines
3. Ensure all tests pass
4. Update documentation if needed
5. Submit a pull request with a clear description
6. Request review from maintainers

## Questions?

For questions or clarifications, please contact the maintainer:
**Akshay NP** - Stabilix Solutions
