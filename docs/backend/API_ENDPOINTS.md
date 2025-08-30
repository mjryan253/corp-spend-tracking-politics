# API Endpoints Reference

## Overview

The Corporate Spending Tracker API provides comprehensive access to corporate spending data across lobbying, political contributions, charitable grants, and financial information. All endpoints support filtering, searching, and pagination.

**Base URL**: `http://localhost:8000/api/` (when running locally)  
**Base URL**: `http://your-domain:8000/api/` (when deployed)

## 🚀 Auto-Generated Documentation

This API now features **auto-generated documentation** using **drf-spectacular** that stays in sync with your code automatically!

### 📖 Access Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs/ - Interactive API explorer with testing capabilities
- **ReDoc**: http://localhost:8000/api/redoc/ - Clean, responsive documentation interface  
- **Raw Schema**: http://localhost:8000/api/schema/ - OpenAPI 3.0 JSON schema

### 🎯 Features of Auto-Generated Docs

- **Real-time Updates**: Documentation automatically updates when you modify your code
- **Interactive Testing**: Test endpoints directly from the Swagger UI
- **Request/Response Examples**: See actual data structures and examples
- **Parameter Validation**: Built-in parameter validation and type checking
- **Authentication Support**: Test with different authentication methods
- **Export Capabilities**: Export schemas for external tools (Postman, Insomnia, etc.)

### 🔧 Generate Static Schema Files

```bash
# Generate JSON schema for external tools
python manage.py spectacular --file api_schema.json --format openapi-json

# Generate YAML schema
python manage.py spectacular --file api_schema.yaml --format openapi

# Use our custom command with statistics
python manage.py generate_schema --output api_schema.json --format openapi-json
```

### 🔗 Integration with External Tools

- **Postman**: Import the JSON schema for automatic collection generation
- **Insomnia**: Import the YAML schema for API testing
- **Code Generation**: Generate client libraries using OpenAPI generators

---

## Authentication

The API supports both session authentication and basic authentication:
- **Session Auth**: Use Django's built-in session authentication
- **Basic Auth**: Include `Authorization: Basic <base64-encoded-credentials>` header

## Common Query Parameters

All list endpoints support these parameters:

- `page`: Page number for pagination (default: 1)
- `page_size`: Number of items per page (default: 20, max: 100)
- `search`: Text search across searchable fields
- `ordering`: Sort by field (prefix with `-` for descending)
- `format`: Response format (`json`, `api`)

## Core Endpoints

### Companies

#### List Companies
```
GET /api/companies/
```

**Query Parameters:**
- `ticker`: Filter by ticker symbol
- `cik`: Filter by SEC CIK
- `headquarters_location`: Filter by headquarters location
- `search`: Search in name, ticker, or CIK
- `ordering`: Sort by name, created_at, updated_at

**Response:**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Apple Inc.",
            "ticker": "AAPL",
            "cik": "0000320193",
            "headquarters_location": "Cupertino, CA",
            "created_at": "2025-08-24T14:00:00Z",
            "updated_at": "2025-08-24T14:00:00Z"
        }
    ]
}
```

#### Get Company Details
```
GET /api/companies/{id}/
```

**Response:**
```json
{
    "id": 1,
    "name": "Apple Inc.",
    "ticker": "AAPL",
    "cik": "0000320193",
    "headquarters_location": "Cupertino, CA",
    "created_at": "2025-08-24T14:00:00Z",
    "updated_at": "2025-08-24T14:00:00Z",
    "financial_summaries": [...],
    "lobbying_reports": [...],
    "charitable_grants": [...]
}
```

#### Company Spending Summary
```
GET /api/companies/{id}/spending_summary/
```

**Query Parameters:**
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)

**Response:**
```json
{
    "company": {
        "id": 1,
        "name": "Apple Inc.",
        "ticker": "AAPL",
        "cik": "0000320193"
    },
    "spending_totals": {
        "lobbying": 2500000.00,
        "charitable": 5000000.00,
        "political": 1000000.00,
        "total": 8500000.00
    },
    "charitable_breakdown": [
        {
            "recipient_category": "Education",
            "total": 3000000.00,
            "count": 15
        }
    ],
    "financial_context": {
        "latest_revenue": 394328000000.00,
        "latest_net_income": 96995000000.00,
        "fiscal_year": 2023
    },
    "record_counts": {
        "lobbying_reports": 12,
        "charitable_grants": 25,
        "political_contributions": 8
    }
}
```

#### Top Spenders
```
GET /api/companies/top_spenders/
```

**Query Parameters:**
- `limit`: Number of companies to return (default: 10)
- `category`: Filter by type (lobbying, charitable, political, all)

**Response:**
```json
[
    {
        "company": {
            "id": 1,
            "name": "Apple Inc.",
            "ticker": "AAPL"
        },
        "spending": {
            "lobbying": 2500000.00,
            "charitable": 5000000.00,
            "political": 1000000.00,
            "total": 8500000.00
        }
    }
]
```

#### Advanced Company Search
```
GET /api/companies/search/
```

**Query Parameters:**
- `q`: Search query (company name, ticker, or CIK)
- `min_spending`: Minimum total spending
- `max_spending`: Maximum total spending
- `has_lobbying`: Filter companies with lobbying data (boolean)
- `has_charitable`: Filter companies with charitable data (boolean)
- `has_political`: Filter companies with political data (boolean)

**Response:**
```json
[
    {
        "id": 1,
        "name": "Apple Inc.",
        "ticker": "AAPL",
        "cik": "0000320193",
        "headquarters_location": "Cupertino, CA"
    }
]
```

### Financial Summaries

#### List Financial Summaries
```
GET /api/financial-summaries/
```

**Query Parameters:**
- `company`: Filter by company ID
- `fiscal_year`: Filter by fiscal year
- `search`: Search in company name or ticker
- `ordering`: Sort by fiscal_year, total_revenue, net_income

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "company": 1,
            "fiscal_year": 2023,
            "total_revenue": 394328000000.00,
            "net_income": 96995000000.00,
            "created_at": "2025-08-24T14:00:00Z",
            "updated_at": "2025-08-24T14:00:00Z"
        }
    ]
}
```

#### Financial Ratios
```
GET /api/financial-summaries/financial_ratios/
```

**Query Parameters:**
- `company`: Filter by company ID
- `year`: Filter by fiscal year

**Response:**
```json
[
    {
        "company": "Apple Inc.",
        "fiscal_year": 2023,
        "revenue": 394328000000.00,
        "net_income": 96995000000.00,
        "profit_margin_percent": 24.6
    }
]
```

### Lobbying Reports

#### List Lobbying Reports
```
GET /api/lobbying-reports/
```

**Query Parameters:**
- `company`: Filter by company ID
- `year`: Filter by year
- `quarter`: Filter by quarter (1-4)
- `search`: Search in company name or specific issues
- `ordering`: Sort by year, quarter, amount_spent, created_at

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "company": 1,
            "year": 2024,
            "quarter": 4,
            "amount_spent": 2500000.00,
            "specific_issues": "Technology, Privacy, Tax Policy",
            "report_url": "https://lda.senate.gov/reports/...",
            "created_at": "2025-08-24T14:00:00Z",
            "updated_at": "2025-08-24T14:00:00Z"
        }
    ]
}
```

#### Lobbying Spending Trends
```
GET /api/lobbying-reports/spending_trends/
```

**Query Parameters:**
- `company`: Filter by company ID
- `start_year`: Start year (default: 2020)
- `end_year`: End year (default: current year)

**Response:**
```json
[
    {
        "year": 2024,
        "quarter": 4,
        "total_spent": 2500000.00,
        "report_count": 3
    }
]
```

#### Top Lobbied Issues
```
GET /api/lobbying-reports/top_issues/
```

**Query Parameters:**
- `limit`: Number of results (default: 10)

**Response:**
```json
[
    {
        "company__name": "Apple Inc.",
        "total_spent": 5000000.00,
        "report_count": 3
    }
]
```

### Political Contributions

#### List Political Contributions
```
GET /api/political-contributions/
```

**Query Parameters:**
- `election_cycle`: Filter by election cycle
- `recipient_party`: Filter by recipient party
- `search`: Search in company PAC ID or recipient name
- `ordering`: Sort by date, amount, election_cycle

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "company_pac_id": "Apple Inc. PAC",
            "recipient_name": "John Smith",
            "recipient_party": "Democratic",
            "amount": 5000.00,
            "date": "2024-10-15",
            "election_cycle": "2024",
            "created_at": "2025-08-24T14:00:00Z",
            "updated_at": "2025-08-24T14:00:00Z"
        }
    ]
}
```

#### Contribution Trends
```
GET /api/political-contributions/contribution_trends/
```

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `election_cycle`: Filter by election cycle

**Response:**
```json
[
    {
        "month": "2024-01-01T00:00:00Z",
        "total_amount": 250000.00,
        "contribution_count": 5
    }
]
```

#### Party Breakdown
```
GET /api/political-contributions/party_breakdown/
```

**Query Parameters:**
- `election_cycle`: Filter by election cycle

**Response:**
```json
[
    {
        "recipient_party": "Democratic",
        "total_amount": 150000.00,
        "contribution_count": 3
    }
]
```

### Charitable Grants

#### List Charitable Grants
```
GET /api/charitable-grants/
```

**Query Parameters:**
- `company`: Filter by company ID
- `fiscal_year`: Filter by fiscal year
- `recipient_category`: Filter by recipient category
- `search`: Search in company name, recipient name, or grant description
- `ordering`: Sort by fiscal_year, amount, created_at

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "company": 1,
            "recipient_name": "Red Cross",
            "recipient_ein": "53-0196605",
            "amount": 1000000.00,
            "fiscal_year": 2024,
            "grant_description": "Disaster relief funding",
            "recipient_category": "Humanitarian",
            "created_at": "2025-08-24T14:00:00Z",
            "updated_at": "2025-08-24T14:00:00Z"
        }
    ]
}
```

#### Grant Category Breakdown
```
GET /api/charitable-grants/category_breakdown/
```

**Query Parameters:**
- `company`: Filter by company ID
- `fiscal_year`: Filter by fiscal year

**Response:**
```json
[
    {
        "recipient_category": "Humanitarian",
        "total_amount": 2000000.00,
        "grant_count": 5
    }
]
```

#### Grant Trends
```
GET /api/charitable-grants/grant_trends/
```

**Query Parameters:**
- `company`: Filter by company ID
- `start_year`: Start year (default: 2020)
- `end_year`: End year (default: current year)

**Response:**
```json
[
    {
        "fiscal_year": 2024,
        "total_amount": 5000000.00,
        "grant_count": 25
    }
]
```

## Analytics Endpoints

### Overall Analytics

#### Dashboard Summary
```
GET /api/analytics/dashboard/
```

**Response:**
```json
{
    "total_companies": 150,
    "total_spending": 500000000.00,
    "spending_breakdown": {
        "lobbying": 200000000.00,
        "political": 150000000.00,
        "charitable": 150000000.00
    },
    "recent_activity": {
        "new_companies": 5,
        "new_reports": 25,
        "new_contributions": 100
    }
}
```

#### Spending Comparison
```
GET /api/analytics/spending_comparison/
```

**Response:**
```json
{
    "results": [
        {
            "company": {
                "id": 1,
                "name": "Apple Inc.",
                "ticker": "AAPL"
            },
            "spending": {
                "lobbying": 2500000.00,
                "charitable": 5000000.00,
                "political": 1000000.00,
                "total": 8500000.00
            }
        }
    ]
}
```

## System Endpoints

### Frontend Logging
```
POST /api/logs/
```

**Request Body:**
```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "INFO",
    "message": "User performed search",
    "data": {"query": "apple", "results": 5},
    "userAgent": "Mozilla/5.0...",
    "url": "/search"
}
```

**Response:**
```json
{
    "status": "success"
}
```

### Get Logs
```
GET /api/logs/get/
```

**Response:**
```json
{
    "logs": [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "level": "INFO",
            "message": "User performed search",
            "data": {"query": "apple", "results": 5},
            "user_agent": "Mozilla/5.0...",
            "url": "/search"
        }
    ]
}
```

## Error Responses

### Standard Error Format
```json
{
    "error": "Error message",
    "detail": "Detailed error information",
    "code": "ERROR_CODE"
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

- **Default**: 1000 requests per hour per IP
- **Authenticated**: 5000 requests per hour per user
- **Admin**: 10000 requests per hour per user

## Examples

### Search for Apple Inc.
```bash
curl "http://localhost:8000/api/companies/search/?q=apple"
```

### Get Apple's spending summary
```bash
curl "http://localhost:8000/api/companies/1/spending_summary/"
```

### Get top 10 spenders
```bash
curl "http://localhost:8000/api/companies/top_spenders/?limit=10"
```

### Get lobbying trends for 2024
```bash
curl "http://localhost:8000/api/lobbying-reports/spending_trends/?start_year=2024&end_year=2024"
```

### Get charitable grants by category
```bash
curl "http://localhost:8000/api/charitable-grants/category_breakdown/"
```

### Test the dashboard analytics
```bash
curl "http://localhost:8000/api/analytics/dashboard/"
```

### Get spending comparison data
```bash
curl "http://localhost:8000/api/analytics/spending_comparison/"
```

---

## 🔧 Development & Customization

### Auto-Generated Documentation Features

The auto-generated documentation includes:

- **Complete API Endpoints**: All ViewSet actions and custom endpoints
- **Request/Response Schemas**: Based on your serializers
- **Query Parameters**: From filters, search, and pagination
- **Path Parameters**: From URL patterns
- **Authentication**: If configured
- **Examples**: From serializer fields and docstrings
- **Tags**: Organized by endpoint categories
- **Descriptions**: From docstrings and decorators

### Schema Configuration

The documentation is configured in `settings.py` with comprehensive settings:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Corporate Spending Tracker API',
    'DESCRIPTION': 'Comprehensive API for accessing corporate spending data...',
    'VERSION': '1.0.0',
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

### Adding New Endpoints

When you add new endpoints, they automatically appear in the documentation. For enhanced documentation, use decorators:

```python
@extend_schema(
    tags=['companies'],
    summary="Get company details",
    description="Retrieve detailed information about a specific company",
    parameters=[
        OpenApiParameter(name='include_spending', type=OpenApiTypes.BOOL, description='Include spending data'),
    ],
    responses={
        200: CompanyDetailSerializer,
        404: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    }
)
def retrieve(self, request, pk=None):
    """Get detailed company information."""
    # Your view logic here
```

### Schema Validation

Validate your schema:
```bash
python manage.py spectacular --validate
```

### Export for External Tools

Export schemas for external API testing tools:
```bash
# For Postman
python manage.py spectacular --file postman_schema.json --format openapi-json

# For Insomnia
python manage.py spectacular --file insomnia_schema.yaml --format openapi
```

---

## 📚 Additional Resources

- **Interactive Documentation**: http://localhost:8000/api/docs/
- **ReDoc Interface**: http://localhost:8000/api/redoc/
- **Raw Schema**: http://localhost:8000/api/schema/
- **drf-spectacular Documentation**: https://drf-spectacular.readthedocs.io/
- **OpenAPI Specification**: https://swagger.io/specification/

This API documentation is now **automatically maintained** and stays in sync with your code. The interactive documentation provides the most up-to-date information about all endpoints, parameters, and response formats.
