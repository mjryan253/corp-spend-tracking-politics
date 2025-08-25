# Corporate Spending Tracker - Docker Setup

A minimal Docker setup for running the Corporate Spending Tracker application.

## Overview

This repository has been stripped down to the minimum required to run the frontend and backend in a single Docker stack. The setup includes:

- **Backend**: Django REST API with PostgreSQL database connection
- **Frontend**: Static HTML/JS application served via Python HTTP server
- **Database**: External PostgreSQL at `jwst.domain.castle:5432`

## Quick Start

1. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

2. **Build and run the application**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Admin Panel: http://localhost:8000/admin/

## Services

- **Backend**: Django REST API running on port 8000
  - Automatically runs migrations on startup
  - Creates superuser if not exists
  - Connects to external PostgreSQL database
- **Frontend**: Static HTML/JS served on port 3000
  - Uses Python HTTP server (no nginx required)
  - Serves the main application interface

## Environment Variables

The application expects a `.env` file with the following variables:

```bash
# Database Configuration
DB_HOST=jwst.domain.castle
DB_PORT=5432
DB_NAME=corp_spend_tracker
DB_USER=postgres
DB_PASSWORD=your_actual_password_here

# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,jwst.domain.castle

# Optional: Use SQLite for development
USE_SQLITE=false
```

## Database

The application connects to a PostgreSQL database at `jwst.domain.castle:5432`. Make sure the database is accessible and the credentials in your `.env` file are correct.

### Database Connection Issues

If you see authentication errors like:
```
FATAL: password authentication failed for user "postgres"
```

1. **Check your .env file**: Make sure `DB_PASSWORD` is set to the correct password
2. **Verify database access**: Ensure the database at `jwst.domain.castle:5432` is accessible from your Docker host
3. **Test connection manually**: Try connecting with a PostgreSQL client to verify credentials
4. **Use SQLite for development**: Set `USE_SQLITE=true` in your `.env` file to use a local SQLite database

## What Was Removed

To create this minimal setup, the following components were removed or simplified:

- **Nginx**: Replaced with Python HTTP server for frontend
- **Database container**: Uses external database instead
- **Complex initialization**: Simplified startup process
- **Development scripts**: Removed unnecessary deployment scripts
- **Documentation**: Kept only essential Docker documentation

## Development

To run in development mode with auto-reload:

```bash
docker-compose up --build
```

To stop the services:

```bash
docker-compose down
```

To view logs:

```bash
docker-compose logs backend
docker-compose logs frontend
```

## Troubleshooting

### Common Issues

**Database Connection Errors:**
- Check your database credentials in the `.env` file
- Ensure the database server is accessible from your Docker host
- Try using SQLite for development: set `USE_SQLITE=true` in `.env`

**Backend Startup Issues:**
- The backend will automatically run migrations and create a superuser on first startup
- If database connection fails, the backend will start but may not function properly
- Check container logs: `docker-compose logs backend`

**Frontend Issues:**
- The frontend is served on port 3000 via Python HTTP server
- Check container logs: `docker-compose logs frontend`

### Using SQLite for Development

If you can't connect to the PostgreSQL database, you can use SQLite for development:

1. Edit your `.env` file:
   ```bash
   USE_SQLITE=true
   # Comment out or remove PostgreSQL settings
   # DB_HOST=jwst.domain.castle
   # DB_PASSWORD=your_password
   ```

2. Rebuild and restart:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

## File Structure

```
├── docker-compose.yml          # Main Docker Compose configuration
├── .dockerignore              # Docker build exclusions
├── env.example                # Environment variables template
├── README_DOCKER.md           # This documentation
├── backend/
│   ├── Dockerfile             # Backend container definition
│   ├── start.sh               # Backend startup script
│   ├── requirements.txt       # Python dependencies
│   └── ...                    # Django application files
└── frontend/
    ├── Dockerfile             # Frontend container definition
    ├── index.html             # Main application interface
    └── logger.js              # Frontend logging utility
```
