# Enterprise Architecture Documentation

## Project Structure

This project follows **Clean Architecture** and **Dependency Injection** principles for enterprise-grade Python applications.

```
app/
├── api/                    # API/Presentation Layer
│   └── v1/                 # API versioning
│       └── worklogs.py     # Worklog endpoints
├── domain/                 # Domain/Business Layer
│   ├── interfaces.py       # Abstract interfaces (contracts)
│   ├── repositories/       # Data access abstractions
│   │   └── worklog_repository.py
│   └── services/          # Business logic
│       └── worklog_service.py
├── infrastructure/         # Infrastructure/External Layer
│   └── jira_client.py     # Jira API implementation
├── core/                  # Core/Shared Layer
│   ├── container.py       # Dependency Injection Container
│   ├── config.py          # Configuration
│   ├── dependencies.py    # FastAPI dependencies
│   ├── auth.py            # Authentication logic
│   └── session.py         # Session management
├── models/                # Data Models
│   └── worklog.py
├── services/              # Legacy services (deprecated - use domain/services)
├── utils/                 # Utility functions
├── auth/                  # Authentication routes
├── ui/                    # UI routes
└── main.py                # Application entry point
```

## Architecture Layers

### 1. **API Layer** (`app/api/`)
- **Purpose**: HTTP endpoints and request/response handling
- **Responsibilities**:
  - Route definitions
  - Request validation
  - Response formatting
  - Dependency injection setup
- **Dependencies**: Domain interfaces, Core dependencies

### 2. **Domain Layer** (`app/domain/`)
- **Purpose**: Business logic and domain rules
- **Components**:
  - **Interfaces**: Abstract contracts (`IJiraClient`, `IWorklogService`, `IWorklogRepository`)
  - **Services**: Business logic implementation
  - **Repositories**: Data access abstractions
- **Dependencies**: None (pure business logic)

### 3. **Infrastructure Layer** (`app/infrastructure/`)
- **Purpose**: External integrations and implementations
- **Components**:
  - `JiraClient`: Jira API client implementation
- **Dependencies**: Domain interfaces

### 4. **Core Layer** (`app/core/`)
- **Purpose**: Shared utilities and cross-cutting concerns
- **Components**:
  - `Container`: Dependency Injection container
  - `config`: Configuration management
  - `dependencies`: FastAPI dependencies
  - `auth`: Authentication logic
  - `session`: Session management

## Dependency Injection

### Container Pattern
The `Container` class manages object creation and dependency resolution:

```python
from app.core.container import Container
from app.domain.interfaces import IWorklogService

# Get service with dependencies automatically resolved
service = Container.get_worklog_service_for_user(user)
```

### FastAPI Integration
Dependencies are injected via FastAPI's `Depends()`:

```python
@router.post("/summary")
def get_summary(
    service: IWorklogService = Depends(get_worklog_service)
):
    return service.get_worklog_summary(...)
```

## Benefits

1. **Testability**: Interfaces allow easy mocking
2. **Maintainability**: Clear separation of concerns
3. **Scalability**: Easy to add new features
4. **Flexibility**: Swap implementations without changing business logic
5. **Enterprise Standards**: Follows industry best practices

## Design Patterns Used

- **Dependency Injection**: Via Container and FastAPI Depends
- **Repository Pattern**: Data access abstraction
- **Service Layer Pattern**: Business logic encapsulation
- **Interface Segregation**: Clear contracts via interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions
