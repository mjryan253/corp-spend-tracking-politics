# API Endpoints Reference

## Overview

The Corporate Spending Tracker API provides comprehensive access to corporate spending data across lobbying, political contributions, charitable grants, and financial information. All endpoints support filtering, searching, and pagination.

**Base URL**: `http://localhost:8000/api/` (when running locally)
**Base URL**: `http://your-domain:8000/api/` (when deployed)

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
        "lobbying": 2500000,
        "political_contributions": 1500000,
        "charitable_grants": 5000000
    },
    "spending_breakdown": {
        "lobbying_by_quarter": {...},
        "political_by_cycle": {...},
        "charitable_by_category": {...}
    }
}
```

#### Top Spenders
```
GET /api/companies/top_spenders/
```

**Query Parameters:**
- `spending_type`: Filter by type (lobbying, political, charitable, all)
- `limit`: Number of companies to return (default: 10)
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)

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
            "total_spending": 9000000,
            "lobbying": 2500000,
            "political": 1500000,
            "charitable": 5000000
        }
    ]
}
```

#### Company Search
```
GET /api/companies/search/
```

**Query Parameters:**
- `q`: Search query (company name, ticker, or CIK)
- `limit`: Number of results (default: 10)

**Response:**
```json
{
    "results": [
        {
            "id": 1,
            "name": "Apple Inc.",
            "ticker": "AAPL",
            "cik": "0000320193",
            "headquarters_location": "Cupertino, CA"
        }
    ]
}
```

### Financial Summaries

#### List Financial Summaries
```
GET /api/financial-summaries/
```

**Query Parameters:**
- `company`: Filter by company ID
- `filing_date`: Filter by filing date
- `revenue_min`: Minimum revenue
- `revenue_max`: Maximum revenue
- `net_income_min`: Minimum net income
- `net_income_max`: Maximum net income
- `ordering`: Sort by filing_date, revenue, net_income

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "company": 1,
            "filing_date": "2024-12-31",
            "revenue": 394328000000,
            "net_income": 96995000000,
            "total_assets": 352755000000,
            "total_liabilities": 287912000000,
            "filing_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000010/aapl-20240928.htm"
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
- `ratio_type`: Filter by ratio type (profitability, liquidity, efficiency)

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
            "ratios": {
                "profit_margin": 0.246,
                "return_on_assets": 0.275,
                "debt_to_equity": 0.816,
                "current_ratio": 1.225
            }
        }
    ]
}
```

### Lobbying Reports

#### List Lobbying Reports
```
GET /api/lobbying-reports/
```

**Query Parameters:**
- `company`: Filter by company ID
- `registrant`: Filter by registrant name
- `quarter`: Filter by quarter (YYYY-Q1, YYYY-Q2, etc.)
- `amount_min`: Minimum amount spent
- `amount_max`: Maximum amount spent
- `ordering`: Sort by quarter, amount_spent

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "company": 1,
            "registrant": "Apple Inc.",
            "quarter": "2024-Q4",
            "amount_spent": 2500000,
            "issues": ["Technology", "Privacy", "Tax Policy"],
            "lobbyists": ["John Doe", "Jane Smith"]
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
- `start_quarter`: Filter from quarter
- `end_quarter`: Filter to quarter
- `group_by`: Group by quarter, year, or company

**Response:**
```json
{
    "results": [
        {
            "quarter": "2024-Q4",
            "total_spending": 2500000,
            "company_count": 1,
            "registrant_count": 1
        }
    ]
}
```

#### Top Lobbied Issues
```
GET /api/lobbying-reports/top_issues/
```

**Query Parameters:**
- `limit`: Number of issues to return (default: 10)
- `start_quarter`: Filter from quarter
- `end_quarter`: Filter to quarter

**Response:**
```json
{
    "results": [
        {
            "issue": "Technology",
            "total_spending": 5000000,
            "company_count": 2,
            "report_count": 3
        }
    ]
}
```

### Political Contributions

#### List Political Contributions
```
GET /api/political-contributions/
```

**Query Parameters:**
- `company`: Filter by company ID
- `committee`: Filter by committee name
- `recipient`: Filter by recipient name
- `amount_min`: Minimum contribution amount
- `amount_max`: Maximum contribution amount
- `date_min`: Filter from date
- `date_max`: Filter to date
- `ordering`: Sort by date, amount

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "company": 1,
            "committee": "Apple Inc. PAC",
            "recipient": "John Smith",
            "amount": 5000,
            "date": "2024-10-15",
            "party": "Democratic",
            "state": "CA"
        }
    ]
}
```

#### Contribution Trends
```
GET /api/political-contributions/contribution_trends/
```

**Query Parameters:**
- `company`: Filter by company ID
- `start_date`: Filter from date
- `end_date`: Filter to date
- `group_by`: Group by month, quarter, year, or party

**Response:**
```json
{
    "results": [
        {
            "period": "2024-Q4",
            "total_amount": 1500000,
            "contribution_count": 150,
            "company_count": 1
        }
    ]
}
```

#### Party Breakdown
```
GET /api/political-contributions/party_breakdown/
```

**Query Parameters:**
- `company`: Filter by company ID
- `start_date`: Filter from date
- `end_date`: Filter to date

**Response:**
```json
{
    "results": [
        {
            "party": "Democratic",
            "total_amount": 800000,
            "contribution_count": 80
        },
        {
            "party": "Republican",
            "total_amount": 700000,
            "contribution_count": 70
        }
    ]
}
```

### Charitable Grants

#### List Charitable Grants
```
GET /api/charitable-grants/
```

**Query Parameters:**
- `company`: Filter by company ID
- `foundation`: Filter by foundation name
- `recipient`: Filter by recipient name
- `category`: Filter by grant category
- `amount_min`: Minimum grant amount
- `amount_max`: Maximum grant amount
- `date_min`: Filter from date
- `date_max`: Filter to date
- `ordering`: Sort by date, amount

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "company": 1,
            "foundation": "Apple Foundation",
            "recipient": "Red Cross",
            "amount": 1000000,
            "date": "2024-12-01",
            "category": "Humanitarian",
            "description": "Disaster relief funding"
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
- `start_date`: Filter from date
- `end_date`: Filter to date

**Response:**
```json
{
    "results": [
        {
            "category": "Humanitarian",
            "total_amount": 2000000,
            "grant_count": 5
        },
        {
            "category": "Education",
            "total_amount": 1500000,
            "grant_count": 3
        }
    ]
}
```

#### Grant Trends
```
GET /api/charitable-grants/grant_trends/
```

**Query Parameters:**
- `company`: Filter by company ID
- `start_date`: Filter from date
- `end_date`: Filter to date
- `group_by`: Group by month, quarter, year, or category

**Response:**
```json
{
    "results": [
        {
            "period": "2024-Q4",
            "total_amount": 5000000,
            "grant_count": 10,
            "company_count": 1
        }
    ]
}
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
    "total_spending": 500000000,
    "spending_breakdown": {
        "lobbying": 200000000,
        "political": 150000000,
        "charitable": 150000000
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

**Query Parameters:**
- `companies`: Comma-separated list of company IDs
- `spending_type`: Type to compare (lobbying, political, charitable, all)
- `period`: Time period (year, quarter, month)

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
                "lobbying": 2500000,
                "political": 1500000,
                "charitable": 5000000,
                "total": 9000000
            }
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
curl "http://localhost:8000/api/lobbying-reports/spending_trends/?start_quarter=2024-Q1&end_quarter=2024-Q4"
```

### Get charitable grants by category
```bash
curl "http://localhost:8000/api/charitable-grants/category_breakdown/"
```
