
# Corporate Spending Tracker

A comprehensive web application that tracks and analyzes corporate spending across lobbying, political contributions, and charitable giving by synthesizing data from multiple U.S. government sources.

## Project Overview

This application provides a transparent view of corporate influence by collecting, linking, and displaying data from:

  * **🏛️ Lobbying Expenditures**: U.S. Senate Lobbying Disclosure Act (LDA) Database.
  * **🗳️ Political Contributions**: Federal Election Commission (FEC).
  * **🙏 Charitable & Religious Spending**: IRS Database of Tax-Exempt Organizations.
  * **💰 Corporate Financial Context**: SEC EDGAR.

The backend is built with **Django** and **PostgreSQL**, providing a robust API, while the frontend is a lightweight, responsive interface built with **Alpine.js** and **Tailwind CSS**.

## 🚀 Quick Start

### Prerequisites

  * Docker and Docker Compose

### Quick Start

1.  **Clone the repository**:

     ```
     git clone https://github.com/mjryan253/corp-spend-tracking-politics
     cd corp-spend-tracking-politics
     ```

2.  **Set up environment variables**:
    Copy the example environment file. This file contains the default configuration to connect to the backend services.

    ```bash
    cp env.example .env
    ```

    Update the `.env` file with your database credentials, especially the `DB_PASSWORD`.

3.  **Build and run the application**:

    ```bash
    docker-compose up --build
    ```

4.  **Access the application**:

             * **Frontend**: http://localhost:3000
       * **Backend API**: http://localhost:8000/api/
       * **Admin Panel**: http://localhost:8000/admin/ (user: `admin`, pass: `admin123`)

## 📚 API Documentation

### Auto-Generated Documentation

This project features **auto-generated API documentation** using **drf-spectacular** that automatically stays in sync with your code!

- **Swagger UI**: http://localhost:8000/api/docs/ - Interactive API explorer with testing capabilities
- **ReDoc**: http://localhost:8000/api/redoc/ - Clean, responsive documentation interface  
- **Raw Schema**: http://localhost:8000/api/schema/ - OpenAPI 3.0 JSON schema

### API Features

- **24 API Endpoints** automatically documented
- **Interactive Testing**: Test endpoints directly from Swagger UI
- **Real-time Updates**: Documentation automatically updates when code changes
- **Export Capabilities**: Generate schemas for external tools (Postman, Insomnia, etc.)

### Generate Schema Files

```bash
# Generate JSON schema for external tools
python manage.py spectacular --file api_schema.json --format openapi-json

# Generate YAML schema
python manage.py spectacular --file api_schema.yaml --format openapi

# Use our custom command with statistics
python manage.py generate_schema --output api_schema.json --format openapi-json
```

For complete API details, see **[API Documentation](API_ENDPOINTS.md)**.

## 🔧 Configuration

### Environment Variables

The application uses environment variables for configuration, loaded from `.env`:

```bash
# Database Configuration
DB_NAME=dev_postgres_db_tracker
DB_USER=some_user
DB_PASSWORD=superdupersecretpassword1!
DB_HOST=jwst.domain.castle
DB_PORT=5432
USE_SQLITE=false

# Django Configuration
SECRET_KEY=django-insecure-r55(7n1p8aad8d!)u_&6-4@!glt!ba!o93#%gajl(^8h^r9f#a
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,jwst.domain.castle

# API Keys (optional for development)
FEC_API_KEY=your_fec_api_key_here
PROPUBLICA_API_KEY=your_propublica_api_key_here
SEC_API_KEY=your_sec_api_key_here
```

### API Keys for Real Data

The application can run entirely with sample data out-of-the-box. To ingest real-time data from government sources, you will need to acquire free API keys:

  * **`FEC_API_KEY`**: For political contributions from [FEC API](https://api.open.fec.gov/developers/)
  * **`PROPUBLICA_API_KEY`**: For charitable grants from [ProPublica](https://www.propublica.org/datastore/api)
  * **`SEC_API_KEY`**: For corporate financial data from [SEC-API.io](https://sec-api.io/)

For detailed configuration instructions, see **[In-Depth Configuration Guide](backend/in-depth-configuration.md)**.

## 📊 Data Ingestion

The application features a powerful data ingestion pipeline to collect and process data. You can control it using Django management commands.

```bash
# Test the ingestion pipeline (uses mock data if no API keys are set)
docker-compose exec backend python manage.py test_ingestion

# Populate the database with initial sample data
docker-compose exec backend python manage.py create_sample_data

# Run the full data ingestion (requires API keys for real data)
docker-compose exec backend python manage.py ingest_data
```

### Data Sources

#### 1. Federal Election Commission (FEC) API
- **Purpose**: Political contribution data from corporate PACs
- **Rate Limits**: 1,000 requests per hour (free tier)
- **Authentication**: API Key required

#### 2. Senate Lobbying Disclosure Act (LDA) Database
- **Purpose**: Lobbying expenditures and reports
- **Rate Limits**: Not specified
- **Authentication**: None required (public data)

#### 3. IRS/ProPublica Nonprofit API
- **Purpose**: Charitable grants and foundation data
- **Rate Limits**: 5,000 requests per month (free tier)
- **Authentication**: API Key required

#### 4. SEC EDGAR via SEC-API.io
- **Purpose**: Corporate financial data and filings
- **Rate Limits**: Varies by plan (free tier: 100 requests/month)
- **Authentication**: API Key required

## 🏗️ Architecture

### Containerized Setup

The application is containerized using Docker Compose with two main services:

**Backend Service**:
- **Image**: Python 3.11-slim
- **Port**: 8000
- **Database**: PostgreSQL (external at `jwst.domain.castle:5432`)
- **Environment**: Loaded from `.env`
- **Startup**: Automatic migrations, superuser creation, static file collection

**Frontend Service**:
- **Image**: Python 3.11-slim with HTTP server
- **Port**: 3000
- **Proxy**: Serves static files and proxies API requests to backend

### Database Configuration
- **Primary**: PostgreSQL at `jwst.domain.castle:5432`
- **Fallback**: SQLite (set `USE_SQLITE=true` in `.env`)
- **Migrations**: Automatic on container startup
- **Superuser**: Auto-created if not exists

## 🔗 External Tool Integration

### Export for External Tools

```bash
# For Postman
python manage.py spectacular --file postman_schema.json --format openapi-json

# For Insomnia
python manage.py spectacular --file insomnia_schema.yaml --format openapi
```

### Supported Tools
- **Postman**: Import JSON schema for automatic collection generation
- **Insomnia**: Import YAML schema for API testing
- **Code Generation**: Generate client libraries using OpenAPI generators

## 🐛 Troubleshooting

### Common Issues

**Database Connection Errors**:
```
Error: connection to server at "jwst.domain.castle" failed
Solution: Check database credentials in .env
```

**API Key Errors**:
```
Error: 403 Forbidden
Solution: Verify API key is correct and active
```

**Rate Limit Exceeded**:
```
Error: 429 Too Many Requests
Solution: Implement rate limiting or upgrade API plan
```

### Debug Commands

```bash
# View container logs
docker-compose logs backend
docker-compose logs frontend

# Access backend container
docker-compose exec backend python manage.py shell

# Test data ingestion
docker-compose exec backend python manage.py test_ingestion

# Validate API schema
docker-compose exec backend python manage.py spectacular --validate
```

## 📈 Features

### Auto-Generated Documentation
- **Zero Maintenance**: Documentation automatically stays in sync
- **Interactive Testing**: Test endpoints directly from Swagger UI
- **Type Safety**: Built-in parameter validation
- **Real-time Updates**: No manual documentation updates needed

### Data Processing
- **Company Linking**: Automatic name normalization across data sources
- **Grant Classification**: Automatic categorization of charitable grants
- **Data Quality Monitoring**: Comprehensive quality metrics and validation
- **Error Handling**: Robust error handling with recovery strategies

### Analytics
- **Dashboard Summary**: Comprehensive statistics and spending breakdown
- **Spending Comparison**: Compare spending across companies and categories
- **Trends Analysis**: Historical spending trends and patterns
- **Top Spenders**: Identify highest spending companies

## 🚀 Future Enhancements

### Planned Features
- Machine learning for company name matching
- Real-time data updates
- Advanced analytics and reporting
- Data visualization dashboards
- Export functionality
- Webhook notifications

### Scalability Improvements
- Distributed processing
- Database sharding
- Caching layer
- Load balancing
- Microservices architecture

## 📚 Additional Resources

- **[API Endpoints Reference](API_ENDPOINTS.md)** - Complete API documentation
- **[In-Depth Configuration Guide](backend/in-depth-configuration.md)** - Detailed configuration and setup
- **[Auto-Generated API Docs Summary](AUTO_GENERATED_API_DOCS_SUMMARY.md)** - Implementation details

## 🤝 Support the Project

This is an open-source project dedicated to increasing transparency in corporate spending. If you find it useful, please consider supporting its development. Your support helps cover server costs and allows for continued enhancements.

---

This implementation provides a **production-ready, professional API documentation system** that will automatically stay current with your codebase while providing an excellent developer experience.

