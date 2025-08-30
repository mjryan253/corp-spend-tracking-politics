# Corporate Spending Tracker Documentation

This directory contains comprehensive documentation for the Corporate Spending Tracker project, organized by component and topic.

## 📁 Documentation Structure

### 🏗️ Backend Documentation (`/docs/backend/`)
- **[API Endpoints](backend/API_ENDPOINTS.md)** - Complete API reference with auto-generated documentation, endpoints, examples, and authentication details
- **[In-Depth Configuration](backend/in-depth-configuration.md)** - Detailed backend configuration guide covering containerized architecture, data sources, API connections, and advanced features

### 🎨 Frontend Documentation (`/docs/frontend/`)
- **[Frontend README](frontend/README.md)** - Complete frontend development guide including setup, build process, configuration, technology stack, and deployment instructions

### 📋 General Documentation
- **[Feature Updates Summary](FEATURE_UPDATES_SUMMARY.md)** - Comprehensive summary of recent improvements including error handling, testing, code quality, configuration enhancements, and roadmap verification

## 🚀 Quick Links

### Getting Started
- [Main README](../README.md) - Project overview and quick setup
- [Roadmap & Vision](../roadmap_and_vision.md) - Project goals and future plans
- [Backend Configuration](backend/in-depth-configuration.md) - Detailed setup guide
- [Frontend Setup](frontend/README.md) - Frontend development guide

### API & Development
- [API Documentation](backend/API_ENDPOINTS.md) - Complete API reference
- [Interactive API Docs](http://localhost:8000/api/docs/) - Swagger UI (when running locally)
- [Feature Updates](FEATURE_UPDATES_SUMMARY.md) - Recent improvements and changes

### Architecture Overview

```
Corporate Spending Tracker
├── Backend (Django/Python)
│   ├── REST API with auto-generated docs
│   ├── Data ingestion pipeline
│   ├── PostgreSQL database
│   └── Error handling & monitoring
├── Frontend (Vanilla JS + Alpine.js)
│   ├── Responsive design with Tailwind CSS
│   ├── Interactive charts with Chart.js
│   ├── Modern build system
│   └── Environment-aware configuration
└── Documentation (You are here!)
    ├── Backend guides & API reference
    ├── Frontend development guide
    └── Project updates & features
```

## 📚 Documentation Categories

### Development & Setup
- **[Backend Configuration](backend/in-depth-configuration.md)** - Database setup, Docker configuration, environment variables
- **[Frontend Setup](frontend/README.md)** - Node.js setup, build system, development workflow

### API & Integration
- **[API Endpoints](backend/API_ENDPOINTS.md)** - REST API documentation with examples
- **[Error Handling](FEATURE_UPDATES_SUMMARY.md#error-handling)** - Exponential backoff, circuit breakers, resilience patterns

### Features & Updates
- **[Recent Improvements](FEATURE_UPDATES_SUMMARY.md)** - Latest features, testing enhancements, code quality improvements
- **[Project Vision](../roadmap_and_vision.md)** - Goals, roadmap, and future enhancements

## 🔧 Configuration Quick Reference

### Backend Configuration
```bash
# Database connection
DB_HOST=jwst.domain.castle
DB_NAME=dev_postgres_db_tracker

# API endpoints
http://localhost:8000/api/docs/     # Interactive API docs
http://localhost:8000/api/redoc/    # Alternative docs interface
```

### Frontend Configuration
```bash
# Development
npm run dev                         # Start development server
npm run build                       # Build for production

# API configuration (automatically detected)
# Development: http://127.0.0.1:8000/api
# Production: /api (relative paths)
```

## 🎯 For Developers

### New to the Project?
1. Read the [Main README](../README.md) for project overview
2. Follow [Backend Configuration](backend/in-depth-configuration.md) for setup
3. Review [API Documentation](backend/API_ENDPOINTS.md) for endpoints
4. Check [Frontend Guide](frontend/README.md) for UI development

### Making Changes?
1. Review [Feature Updates](FEATURE_UPDATES_SUMMARY.md) for recent patterns
2. Use [API Documentation](backend/API_ENDPOINTS.md) for endpoint references
3. Follow development workflows in respective component guides

### Deploying?
1. [Backend Configuration](backend/in-depth-configuration.md) - Docker deployment
2. [Frontend Guide](frontend/README.md) - Production build process

---

**Need help?** Check the troubleshooting sections in each component's documentation or refer to the main project README.
