# In-Depth Configuration Guide

## Data Ingestion Pipeline Configuration

This document provides detailed information about the data sources, API connections, and configuration options for the Corporate Spending Tracker's data ingestion pipeline.

## Data Sources Overview

### 1. Federal Election Commission (FEC) API
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

### 2. Senate Lobbying Disclosure Act (LDA) Database
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

### 3. IRS/ProPublica Nonprofit API
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

### 4. SEC EDGAR via SEC-API.io
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

## Troubleshooting

### Common Issues

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

**Network Timeouts**:
```
Error: Connection timeout
Solution: Check network connectivity and API endpoint status
```

**Data Processing Errors**:
```
Error: Invalid date format
Solution: Check data source format and update parsing logic
```

### Debug Commands
```bash
# Test individual data sources
python manage.py test_ingestion

# Check data quality
python manage.py shell -c "from data_collection.ingestion.data_processor import DataProcessor; p = DataProcessor(); print(p.get_data_quality_report())"

# Verify API connections
python manage.py shell -c "from data_collection.ingestion.fec_ingestion import FECIngestion; f = FECIngestion(); print(f.get_committee_info('C00123456'))"
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
