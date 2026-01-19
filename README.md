# Jira Worklog Summary

An internal FastAPI-based application to fetch, aggregate, and visualize
Jira worklogs in a **daily, issue-wise, and worklog-level summary**
format.

This tool is designed for **internal employees** to: - Track how much
time they logged per day - View worklogs grouped by Jira issue - Render
data via both **REST API** and a **simple UI**

## Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Environment Setup](#-environment-setup)
- [Running the Application](#️-running-the-application)
- [API Usage](#-api-usage)
- [UI Usage](#-ui-usage)
- [OAuth Setup](#-oauth-setup)
- [Technology Stack](#-technology-stack)
- [Troubleshooting](#-troubleshooting)
- [Maintainer](#-maintainer)
- [License](#-license)
- [Additional Documentation](#-additional-documentation)

------------------------------------------------------------------------

## ⚡ Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
git clone <repository-url>
cd jira-worklog-summary

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (see Environment Setup section)
cp .env.example .env  # Edit with your credentials

# 5. Run the application
python app/main.py
```

Visit http://localhost:8000/ui/worklogs to get started!

> 📝 **Note**: You'll need to set up OAuth credentials first. See [OAuth Setup](#-oauth-setup) section.

------------------------------------------------------------------------

## 🚀 Features

-   ✅ Daily worklog summary
-   ✅ Issue-level and worklog-level breakdown
-   ✅ Human-readable time formatting (e.g., `8h 30m`)
-   ✅ FastAPI REST endpoint
-   ✅ Simple server-rendered UI (Jinja2)
-   ✅ Environment-based configuration
-   ✅ Cloud-ready architecture

------------------------------------------------------------------------

## 🧱 Project Structure

This project follows **Hexagonal Architecture (Ports & Adapters)** pattern, organizing code into clear layers:

``` text
jira-worklog-summary/
│
├── app/
│   ├── main.py                # FastAPI entry point & app configuration
│   │
│   ├── presentation/          # PRESENTATION LAYER (Routes/Controllers)
│   │   ├── api/              # REST API endpoints
│   │   │   └── v1/
│   │   │       └── worklogs.py
│   │   └── web/              # Web UI routes
│   │       ├── auth.py       # Authentication routes
│   │       └── worklogs.py   # Worklog UI routes
│   │
│   ├── domain/                # DOMAIN LAYER (Business Logic)
│   │   ├── interfaces.py     # Domain interfaces (ports)
│   │   ├── repositories/     # Repository interfaces & implementations
│   │   │   └── worklog_repository.py
│   │   └── services/         # Business logic services
│   │       └── worklog_service.py
│   │
│   ├── infrastructure/        # INFRASTRUCTURE LAYER (Adapters)
│   │   └── jira_client.py    # Jira API client adapter
│   │
│   ├── core/                  # CORE (Shared Utilities)
│   │   ├── config.py         # Configuration
│   │   ├── auth.py           # OAuth authentication logic
│   │   ├── base.py           # Base classes (Repository, Service)
│   │   ├── exceptions.py     # Custom exception hierarchy
│   │   ├── logging.py        # Structured JSON logging
│   │   ├── error_handler.py  # Error handling utilities
│   │   ├── container.py      # Dependency injection
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   └── session.py        # Session management
│   │
│   ├── models/                # Data models (DTOs)
│   │   └── worklog.py
│   │
│   └── utils/                 # Utility functions
│       └── helpers.py
│
├── static/                     # Static files (CSS, JS, images)
├── templates/                  # Jinja2 templates
├── .env                        # Environment variables (not committed)
├── .gitignore                  # Git ignore rules
├── LICENSE                     # License file
├── README.md                   # This file
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── SECURITY.md                 # Security policy
└── requirements.txt            # Python dependencies
```

### Architecture Layers Explained

1. **Presentation Layer** (`presentation/`)
   - **Purpose**: Handles HTTP requests/responses
   - **Contains**: API routes (REST) and Web routes (UI)
   - **Responsibility**: Request validation, response formatting, authentication checks

2. **Domain Layer** (`domain/`)
   - **Purpose**: Core business logic (independent of frameworks)
   - **Contains**: Interfaces, repositories, services
   - **Responsibility**: Business rules, data aggregation, validation

3. **Infrastructure Layer** (`infrastructure/`)
   - **Purpose**: External system adapters
   - **Contains**: Jira API client, database clients (if any)
   - **Responsibility**: Communication with external services

4. **Core** (`core/`)
   - **Purpose**: Shared utilities and cross-cutting concerns
   - **Contains**: Config, logging, exceptions, DI container
   - **Responsibility**: Application-wide functionality

### Design Principles

- **Separation of Concerns**: Each layer has a single responsibility
- **Dependency Inversion**: Domain layer doesn't depend on infrastructure
- **Testability**: Business logic can be tested without HTTP/DB dependencies
- **Maintainability**: Clear boundaries make code easier to understand and modify

------------------------------------------------------------------------

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (Python 3.10+ recommended)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Atlassian Jira account** with appropriate permissions
- **OAuth 2.0 app** created in [Atlassian Developer Console](https://developer.atlassian.com/console)

### System Requirements

- **OS**: Linux, macOS, or Windows
- **RAM**: Minimum 512MB, 1GB recommended
- **Disk Space**: ~100MB for application and dependencies
- **Network**: Internet connection for Jira API access

------------------------------------------------------------------------

## 🔐 Environment Setup

Create a `.env` file at the project root:

``` env
JIRA_DOMAIN=your-domain.atlassian.net
JIRA_OAUTH_CLIENT_ID=your_oauth_client_id
JIRA_OAUTH_CLIENT_SECRET=your_oauth_client_secret
JIRA_OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
SECRET_KEY=your-secret-key-for-session-management
```

### Environment Variables Explained

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `JIRA_DOMAIN` | Your Atlassian Jira domain | Yes | `company.atlassian.net` |
| `JIRA_OAUTH_CLIENT_ID` | OAuth 2.0 Client ID from Atlassian Developer Console | Yes | `abc123...` |
| `JIRA_OAUTH_CLIENT_SECRET` | OAuth 2.0 Client Secret from Atlassian Developer Console | Yes | `xyz789...` |
| `JIRA_OAUTH_REDIRECT_URI` | OAuth callback URL (must match Developer Console settings) | Yes | `http://localhost:8000/auth/callback` |
| `SECRET_KEY` | Secret key for session encryption (use a strong random string) | Yes | `your-secret-key-here` |

> ⚠️ **Security Note**: Never commit `.env` or OAuth credentials to source control. The `.env` file is already included in `.gitignore`.

------------------------------------------------------------------------

## ▶️ Running the Application

### 1️⃣ Create & activate virtual environment

``` bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2️⃣ Install dependencies

``` bash
pip install -r requirements.txt
```

### 3️⃣ Start FastAPI server

``` bash
python app/main.py
```

Server will start at:

    http://localhost:8000

------------------------------------------------------------------------

## 🔌 API Usage

### Authentication

The application uses OAuth 2.0 for authentication. Users must authenticate via the `/auth/login` endpoint before accessing protected endpoints.

### Endpoint

    POST /api/v1/jira-worklogs/summary

**Requires:** Authentication (OAuth token in session)

### Request Body

``` json
{
  "accountId": "557058:abc123",
  "startDate": "2026-01-01",
  "endDate": "2026-01-31"
}
```

### Response

Returns a structured JSON response grouped by: - Day - Issue - Worklog entries

**Example Response:**

``` json
[
  {
    "workDateFormatted": "2026-01-15",
    "daySummary": {
      "totalTimeSpentFormatted": "8h 30m",
      "totalTimeSpentSeconds": 30600
    },
    "issues": [
      {
        "issueKey": "PROJ-123",
        "issueSummary": "Implement feature X",
        "reportedBy": {
          "displayName": "John Doe"
        },
        "worklogSummary": {
          "totalTimeSpentFormatted": "4h 15m",
          "totalTimeSpentSeconds": 15300
        },
        "worklogs": [
          {
            "timeSpentFormatted": "2h 30m",
            "comment": "Initial implementation"
          }
        ]
      }
    ]
  }
]
```

### API Documentation

When running locally, interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

------------------------------------------------------------------------

## 🖥 UI Usage

Open in browser:

    http://localhost:8000/ui/worklogs

You will be redirected to login if not authenticated.

### UI Capabilities

-   OAuth-based authentication with Jira
-   Select date range (with quick filters: Today, This Week, This Month, etc.)
-   View daily summaries with time indicators
-   Expand issue and worklog details
-   Toggle between card view and table view
-   Sticky header for filters
-   Responsive design for mobile and desktop

------------------------------------------------------------------------

## 🛠 Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.8+** - Programming language
- **Jinja2** - Template engine for server-side rendering
- **Authlib** - OAuth 2.0 client library
- **Requests** - HTTP library for API calls
- **Uvicorn** - ASGI server

### Frontend
- **Tailwind CSS** - Utility-first CSS framework
- **Vanilla JavaScript** - No framework dependencies
- **Flatpickr** - Date range picker

### Architecture
- **Hexagonal Architecture** - Clean architecture pattern
- **Dependency Injection** - Loose coupling between components
- **Repository Pattern** - Data access abstraction

### Key Dependencies

- `fastapi==0.128.0` - Web framework
- `authlib==1.3.0` - OAuth 2.0
- `requests==2.32.5` - HTTP client
- `python-dotenv==1.2.1` - Environment variables
- `python-json-logger>=3.2.1` - Structured logging

See [requirements.txt](requirements.txt) for complete dependency list.

------------------------------------------------------------------------

## 🔧 Troubleshooting

### Common Issues

#### 1. OAuth Authentication Fails

**Problem**: "OAuth error: access_denied" or authentication redirect fails.

**Solutions**:
- Verify `JIRA_OAUTH_REDIRECT_URI` matches exactly in Atlassian Developer Console
- Check that OAuth app is active in Developer Console
- Ensure callback URL uses correct protocol (http/https)
- Clear browser cookies and try again

#### 2. "Missing authorization code" Error

**Problem**: Callback returns without authorization code.

**Solutions**:
- Check OAuth app configuration in Developer Console
- Verify redirect URI is whitelisted
- Ensure state parameter validation is working

#### 3. Session Expired Errors

**Problem**: "Session expired. Please login again."

**Solutions**:
- Refresh tokens are automatically handled, but if issue persists:
- Clear browser cookies
- Re-authenticate via `/auth/login`
- Check `SECRET_KEY` is set correctly

#### 4. Port Already in Use

**Problem**: `Address already in use` when starting server.

**Solutions**:
- Change port: `uvicorn app.main:app --port 8001`
- Or kill process using port 8000:
  ```bash
  # Linux/macOS
  lsof -ti:8000 | xargs kill
  
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```

#### 5. Module Not Found Errors

**Problem**: `ModuleNotFoundError` when running application.

**Solutions**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

#### 6. Jira API Rate Limiting

**Problem**: 429 Too Many Requests errors.

**Solutions**:
- The application includes automatic retry logic
- Reduce date range if querying large datasets
- Wait before retrying

### Getting Help

If you encounter issues not covered here:
1. Check the [CHANGELOG.md](CHANGELOG.md) for known issues
2. Review [SECURITY.md](SECURITY.md) for security-related concerns
3. Contact the maintainer: **Akshay NP** at Stabilix Solutions

------------------------------------------------------------------------

## 🔍 OAuth Setup

To set up OAuth authentication:

1. Go to [Atlassian Developer Console](https://developer.atlassian.com/console) and create a new OAuth 2.0 (3LO) app
2. Set the callback URL to match `JIRA_OAUTH_REDIRECT_URI` in your `.env`
3. Copy the Client ID and Client Secret to your `.env` file
4. The app will automatically use the authenticated user's account ID

> 💡 **Note**: The OAuth client app is created in the [Atlassian Developer Console](https://developer.atlassian.com/console). Use this link to access the console and manage your OAuth applications.

------------------------------------------------------------------------
## 👨‍💻 Maintainer

**Akshay NP**\
Stabilix Solutions

------------------------------------------------------------------------

## 📄 License

Copyright (c) 2024 Stabilix Solutions. All Rights Reserved.

This software is proprietary and confidential. Unauthorized copying, modification, 
distribution, or use is strictly prohibited without express written permission.

See [LICENSE](LICENSE) for full license terms.

------------------------------------------------------------------------

## 📚 Additional Documentation

- [CHANGELOG.md](CHANGELOG.md) - Version history and changes
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [SECURITY.md](SECURITY.md) - Security policy and reporting
