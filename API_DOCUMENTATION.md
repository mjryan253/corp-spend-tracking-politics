# API Documentation

## Overview

The Corporate Spending Tracker API provides comprehensive access to corporate spending data across lobbying, political contributions, charitable grants, and financial information. All endpoints support filtering, searching, and pagination.

**Base URL**: `http://127.0.0.1:8000/api/`

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

## Endpoints

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
- `limit`: Number of results (default: 10)
- `category`: Filter by category (all, lobbying, charitable, political)

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

#### Advanced Search
```
GET /api/companies/search/
```

**Query Parameters:**
- `q`: Search query
- `min_spending`: Minimum total spending amount
- `max_spending`: Maximum total spending amount
- `has_lobbying`: Filter companies with lobbying data (true/false)
- `has_charitable`: Filter companies with charitable data (true/false)
- `has_political`: Filter companies with political data (true/false)

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

#### Spending Trends
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
        "year": 2023,
        "quarter": 1,
        "total_spent": 500000.00,
        "report_count": 3
    }
]
```

#### Top Issues
```
GET /api/lobbying-reports/top_issues/
```

**Query Parameters:**
- `limit`: Number of results (default: 10)

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

#### Category Breakdown
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
        "recipient_category": "Education",
        "total_amount": 3000000.00,
        "grant_count": 15
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
        "fiscal_year": 2023,
        "total_amount": 5000000.00,
        "grant_count": 25
    }
]
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid parameters",
    "details": "Field 'amount' must be a positive number"
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error."
}
```

## Rate Limiting

- **Anonymous users**: 100 requests per hour
- **Authenticated users**: 1000 requests per hour

## Examples

### Get Apple's spending summary for 2023
```
GET /api/companies/1/spending_summary/?start_date=2023-01-01&end_date=2023-12-31
```

### Search for companies with high lobbying spending
```
GET /api/companies/search/?min_spending=1000000&has_lobbying=true
```

### Get top 5 charitable grant recipients
```
GET /api/charitable-grants/category_breakdown/?limit=5
```

### Get lobbying trends for Microsoft
```
GET /api/lobbying-reports/spending_trends/?company=2&start_year=2020&end_year=2024
```

## SDK Examples

### Python (requests)
```python
import requests

# Get company details
response = requests.get('http://127.0.0.1:8000/api/companies/1/')
company = response.json()

# Get spending summary
response = requests.get('http://127.0.0.1:8000/api/companies/1/spending_summary/')
summary = response.json()

# Search companies
response = requests.get('http://127.0.0.1:8000/api/companies/search/?q=Apple')
results = response.json()
```

### JavaScript (fetch)
```javascript
// Get company details
const response = await fetch('http://127.0.0.1:8000/api/companies/1/');
const company = await response.json();

// Get spending summary
const summaryResponse = await fetch('http://127.0.0.1:8000/api/companies/1/spending_summary/');
const summary = await summaryResponse.json();

// Search companies
const searchResponse = await fetch('http://127.0.0.1:8000/api/companies/search/?q=Apple');
const results = await searchResponse.json();
```

## Data Models

### Company
- `id`: Primary key
- `name`: Company name
- `ticker`: Stock ticker symbol
- `cik`: SEC Central Index Key
- `headquarters_location`: Company headquarters
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

### FinancialSummary
- `id`: Primary key
- `company`: Foreign key to Company
- `fiscal_year`: Fiscal year
- `total_revenue`: Total revenue
- `net_income`: Net income
- `created_at`: Record creation timestamp

### LobbyingReport
- `id`: Primary key
- `company`: Foreign key to Company
- `year`: Reporting year
- `quarter`: Reporting quarter (1-4)
- `amount_spent`: Amount spent on lobbying
- `specific_issues`: Specific issues lobbied
- `report_url`: URL to original report
- `created_at`: Record creation timestamp

### PoliticalContribution
- `id`: Primary key
- `company_pac_id`: PAC identifier
- `recipient_name`: Recipient name
- `recipient_party`: Recipient party
- `amount`: Contribution amount
- `date`: Contribution date
- `election_cycle`: Election cycle
- `created_at`: Record creation timestamp

### CharitableGrant
- `id`: Primary key
- `company`: Foreign key to Company
- `recipient_name`: Grant recipient name
- `recipient_ein`: Recipient EIN
- `amount`: Grant amount
- `fiscal_year`: Fiscal year
- `grant_description`: Grant description
- `recipient_category`: Recipient category (auto-classified)
- `created_at`: Record creation timestamp
