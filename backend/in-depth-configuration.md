# In-Depth Configuration Guide

## Overview

This document provides detailed information about the Corporate Spending Tracker's containerized architecture, data sources, API connections, configuration options, and advanced features.

## Containerized Architecture

### Docker Setup
The application is containerized using Docker Compose with two main services:

**Backend Service**:
- **Image**: Python 3.11-slim
- **Port**: 8000
- **Database**: PostgreSQL (external at `jwst.domain.castle:5432`)
- **Environment**: Loaded from `backend/.env`
- **Startup**: Automatic migrations, superuser creation, static file collection

**Frontend Service**:
- **Image**: Python 3.11-slim with HTTP server
- **Port**: 3000
- **Proxy**: Serves static files and proxies API requests to backend
- **No nginx**: Uses Python HTTP server for simplicity

### Environment Configuration
The application uses environment variables for configuration, loaded from `backend/.env`:

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

### Database Configuration
- **Primary**: PostgreSQL at `jwst.domain.castle:5432`
- **Fallback**: SQLite (set `USE_SQLITE=true` in `.env`)
- **Migrations**: Automatic on container startup
- **Superuser**: Auto-created if not exists

## Data Ingestion Pipeline Configuration

### Data Sources Overview

#### 1. Federal Election Commission (FEC) API
**Purpose**: Political contribution data from corporate PACs

**API Endpoint**: `https://api.open.fec.gov/v1`
**Authentication**: API Key required
**Rate Limits**: 1,000 requests per hour (free tier)

**Key Endpoints Used**:
- `/schedules/schedule_a/` - Individual contributions
- `/committee/{committee_id}/` - Committee information
- `/committees/` - Committee search

**Configuration**:
```bash
FEC_API_KEY=your_fec_api_key_here
```

**How to Get API Key**:
1. Visit https://api.open.fec.gov/developers/
2. Register for a free account
3. Request an API key
4. Wait for approval (usually 24-48 hours)

**Data Structure**:
- Committee IDs (e.g., C00123456)
- Contribution amounts and dates
- Recipient information
- Contributor details

#### 2. Senate Lobbying Disclosure Act (LDA) Database
**Purpose**: Lobbying expenditures and reports

**API Endpoint**: `https://lda.senate.gov/api/v1`
**Authentication**: None required (public data)
**Rate Limits**: Not specified

**Key Endpoints Used**:
- `/reports` - Quarterly lobbying reports
- `/search` - Company-specific lobbying data
- `/registrants/{id}` - Registrant information

**Configuration**:
```bash
# No API key required for Senate LDA
```

**Data Structure**:
- Registrant (lobbying firm) information
- Client (company) information
- Quarterly spending amounts
- Specific issues lobbied
- Lobbyist names

#### 3. IRS/ProPublica Nonprofit API
**Purpose**: Charitable grants and foundation data

**API Endpoint**: `https://api.propublica.org/nonprofits/v1`
**Authentication**: API Key required
**Rate Limits**: 5,000 requests per month (free tier)

**Key Endpoints Used**:
- `/organizations/{ein}/grants` - Foundation grants
- `/organizations/{ein}` - Organization details
- `/search` - Foundation search

**Configuration**:
```bash
PROPUBLICA_API_KEY=your_propublica_api_key_here
```

**How to Get API Key**:
1. Visit https://www.propublica.org/datastore/api
2. Register for a free account
3. Request API access
4. Receive API key via email

**Data Structure**:
- Foundation EINs (e.g., 13-3398765)
- Grant amounts and recipients
- Recipient categories (auto-classified)
- Fiscal year information

#### 4. SEC EDGAR via SEC-API.io
**Purpose**: Corporate financial data and filings

**API Endpoint**: `https://api.sec-api.io`
**Authentication**: API Key required
**Rate Limits**: Varies by plan (free tier: 100 requests/month)

**Key Endpoints Used**:
- `/query` - Search and retrieve filings
- Company information extraction
- Financial metrics calculation

**Configuration**:
```bash
SEC_API_KEY=your_sec_api_key_here
```

**How to Get API Key**:
1. Visit https://sec-api.io/
2. Sign up for a free account
3. Get API key from dashboard
4. Upgrade plan for higher limits

**Data Structure**:
- Company CIKs (e.g., 0000320193 for Apple)
- 10-K filing data
- Financial metrics (revenue, net income)
- Filing dates and URLs

## Company Linking System

### Name Normalization
The system automatically normalizes company names across different data sources:

**Examples**:
- "Apple Inc." → "apple"
- "APPLE CORPORATION" → "apple"
- "Microsoft Corp" → "microsoft"

**Process**:
1. Convert to lowercase
2. Remove common suffixes (Inc, Corp, LLC, etc.)
3. Remove special characters
4. Standardize whitespace

### Matching Strategies
1. **Exact Name Match**: Primary matching method
2. **Ticker Symbol Match**: Fallback for public companies
3. **CIK Match**: Fallback for SEC-registered companies
4. **Fuzzy Matching**: For similar names (future enhancement)

### Company Mappings
Hardcoded mappings for common variations:
```python
{
    'apple inc': 'Apple Inc.',
    'apple computer': 'Apple Inc.',
    'microsoft corporation': 'Microsoft Corporation',
    'microsoft corp': 'Microsoft Corporation',
    'alphabet inc': 'Alphabet Inc.',
    'google inc': 'Alphabet Inc.',
    'google llc': 'Alphabet Inc.',
}
```

## Charitable Grant Classification

### Automatic Classification Categories
The system automatically categorizes grant recipients based on keywords:

**Religious Organizations**:
- Keywords: church, temple, mosque, synagogue, ministry, mission, catholic, protestant, baptist, methodist, lutheran, presbyterian, episcopal, orthodox, jewish, islamic, hindu, buddhist, religious, faith, spiritual, diocese, archdiocese, parish, congregation

**Educational Institutions**:
- Keywords: university, college, school, academy, institute, foundation, scholarship, education, learning, research, library, museum, training

**Healthcare Organizations**:
- Keywords: hospital, medical, health, clinic, care, treatment, therapy, rehabilitation, wellness, disease, cancer, heart, mental health

**Humanitarian Organizations**:
- Keywords: red cross, salvation army, united way, humanitarian, disaster, relief, emergency, aid, assistance, charity, help, support, community

**Environmental Organizations**:
- Keywords: environment, conservation, wildlife, nature, climate, sustainability, green, ecology, forest, ocean, clean, renewable

**Arts & Cultural Organizations**:
- Keywords: art, museum, gallery, theater, theatre, music, dance, performance, cultural, creative, arts, entertainment

### Classification Process
1. Combine recipient name and grant description
2. Convert to lowercase
3. Search for category keywords
4. Assign first matching category
5. Default to "Other" if no match found

## Auto-Generated API Documentation

### Overview
The application uses **drf-spectacular** to automatically generate comprehensive API documentation that stays in sync with your code.

### Configuration
The documentation is configured in `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # ... other settings
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Corporate Spending Tracker API',
    'DESCRIPTION': 'Comprehensive API for accessing corporate spending data...',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'TAGS': [
        {'name': 'companies', 'description': 'Company management endpoints'},
        {'name': 'analytics', 'description': 'Analytics and reporting endpoints'},
        {'name': 'lobbying', 'description': 'Lobbying report data endpoints'},
        {'name': 'political', 'description': 'Political contribution endpoints'},
        {'name': 'charitable', 'description': 'Charitable grant endpoints'},
        {'name': 'financial', 'description': 'Financial summary endpoints'},
        {'name': 'system', 'description': 'System and logging endpoints'},
    ],
}
```

### URL Configuration
Documentation endpoints are configured in `urls.py`:

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # ... other URLs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

### Access Points
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Raw Schema**: http://localhost:8000/api/schema/

### Management Commands
```bash
# Generate schema with statistics
python manage.py generate_schema

# Validate schema
python manage.py spectacular --validate

# Export for external tools
python manage.py spectacular --file api_schema.json --format openapi-json
python manage.py spectacular --file api_schema.yaml --format openapi
```

## Data Quality Monitoring

### Quality Metrics Tracked
- **Companies**: Total count, with CIK, with ticker
- **Financial Summaries**: Total count, with revenue, with income
- **Lobbying Reports**: Total count, with amount spent
- **Charitable Grants**: Total count, with category
- **Political Contributions**: Total count, with amount

### Data Validation
- Amount validation (positive numbers)
- Date format validation
- Required field checking
- Duplicate detection

## Error Handling

### API Error Handling
- **403 Forbidden**: Invalid API key or rate limit exceeded
- **404 Not Found**: Endpoint or resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Server Error**: API server issues

### Data Processing Errors
- Invalid date formats
- Missing required fields
- Database constraint violations
- Network timeouts

### Recovery Strategies
- Retry with exponential backoff
- Skip problematic records
- Log errors for manual review
- Continue processing other records

## Performance Considerations

### Rate Limiting
- FEC: 1,000 requests/hour
- ProPublica: 5,000 requests/month
- SEC-API: 100 requests/month (free tier)

### Data Volume
- **FEC**: ~2M+ contributions per election cycle
- **Lobbying**: ~10K+ reports per quarter
- **Charitable**: ~1M+ grants per year
- **SEC**: ~10K+ companies with filings

### Optimization Strategies
- Pagination for large datasets
- Parallel processing where possible
- Caching of frequently accessed data
- Incremental updates

## Security Considerations

### API Key Management
- Store keys in environment variables
- Never commit keys to version control
- Rotate keys regularly
- Use different keys for development/production

### Data Privacy
- No PII (Personally Identifiable Information) stored
- Aggregate data for public display
- Secure database connections
- Regular security audits

## Monitoring and Logging

### Logging Levels
- **INFO**: Successful operations
- **WARNING**: Non-critical issues
- **ERROR**: Failed operations
- **DEBUG**: Detailed debugging information

### Metrics to Monitor
- API response times
- Success/failure rates
- Data quality scores
- Processing throughput
- Error rates by source

### Frontend Logging
The application includes a frontend logging system:

```javascript
// Log frontend events
fetch('/api/logs/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        timestamp: new Date().toISOString(),
        level: 'INFO',
        message: 'User performed search',
        data: {query: 'apple', results: 5},
        userAgent: navigator.userAgent,
        url: window.location.href
    })
});
```

## Container Management

### Startup Process
1. **Database Connection**: Wait for PostgreSQL availability
2. **Migrations**: Run Django migrations automatically
3. **Superuser Creation**: Create admin user if not exists
4. **Static Files**: Collect and serve static files
5. **Server Start**: Launch Django development server

### Health Checks
- **Backend**: Django system check every 30 seconds
- **Frontend**: HTTP availability check every 30 seconds
- **Database**: Connection test during startup

### Logging
- **Backend**: Django logs to stdout/stderr
- **Frontend**: HTTP server logs to stdout/stderr
- **Docker**: Container logs accessible via `docker-compose logs`

## Management Commands

### Available Commands
```bash
# Data ingestion
python manage.py test_ingestion          # Test ingestion pipeline
python manage.py create_sample_data      # Create sample data
python manage.py ingest_data             # Run full data ingestion

# System management
python manage.py wait_for_db             # Wait for database connection
python manage.py create_superuser_if_not_exists  # Create admin user

# API documentation
python manage.py generate_schema         # Generate OpenAPI schema
python manage.py spectacular --validate  # Validate schema
```

### Custom Commands
The application includes several custom management commands:

1. **`generate_schema`**: Generate OpenAPI schema with statistics
2. **`wait_for_db`**: Wait for database connection before startup
3. **`create_superuser_if_not_exists`**: Create admin user if not exists
4. **`test_ingestion`**: Test the data ingestion pipeline
5. **`create_sample_data`**: Populate database with sample data
6. **`ingest_data`**: Run full data ingestion from all sources

## Troubleshooting

### Common Issues

**Database Connection Errors**:
```
Error: connection to server at "jwst.domain.castle" failed
Solution: Check database credentials in backend/.env
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

**Container Startup Issues**:
```
Error: Container fails to start
Solution: Check logs with docker-compose logs backend
```

**Schema Generation Errors**:
```
Error: No module named 'drf_spectacular'
Solution: Install drf-spectacular: pip install drf-spectacular==0.27.0
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

# Check data quality
docker-compose exec backend python manage.py shell -c "from data_collection.ingestion.data_processor import DataProcessor; p = DataProcessor(); print(p.get_data_quality_report())"

# Validate API schema
docker-compose exec backend python manage.py spectacular --validate

# Generate schema with statistics
docker-compose exec backend python manage.py generate_schema
```

### Performance Tuning
```bash
# Monitor database performance
docker-compose exec backend python manage.py shell -c "from django.db import connection; print(connection.queries)"

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/companies/"

# Monitor memory usage
docker stats
```

## Future Enhancements

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

### API Documentation Enhancements
- Custom response examples
- Request body validation
- Authentication documentation
- Rate limiting documentation
- Error code documentation

## External Tool Integration

### Postman
1. Export schema: `python manage.py spectacular --file schema.json --format openapi-json`
2. Import into Postman: File → Import → API Specification

### Insomnia
1. Export schema: `python manage.py spectacular --file schema.yaml --format openapi`
2. Import into Insomnia: Create → Import from File

### Code Generation
Generate client code from your schema:
```bash
# Using openapi-generator
openapi-generator generate -i api_schema.json -g python -o ./client

# Using swagger-codegen
swagger-codegen generate -i api_schema.json -l python -o ./client
```

This comprehensive configuration guide covers all aspects of the Corporate Spending Tracker application, from basic setup to advanced features and troubleshooting.
