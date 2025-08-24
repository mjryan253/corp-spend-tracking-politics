# Corporate Spending Tracker

A comprehensive web application that tracks corporate spending across lobbying, political contributions, and charitable giving by synthesizing data from multiple government sources.

## Project Overview

This application will collect and analyze data from:
- **Lobbying Expenditures**: U.S. Senate Lobbying Disclosure Act (LDA) Database
- **Political Contributions**: Federal Election Commission (FEC) API
- **Charitable & Religious Spending**: IRS Database of Tax-Exempt Organizations
- **Corporate Financial Context**: SEC EDGAR via SEC-API.io

## Technology Stack

- **Backend**: Python with Django and Django REST Framework (DRF)
- **Database**: PostgreSQL (required) with SQLite fallback for development
- **Frontend**: HTML, CSS, and JavaScript with Alpine.js and Tailwind CSS

## API Key Setup

### Getting API Keys

The application can work with real government data if you provide API keys. These are **optional** - the app works perfectly with sample data for development and testing.

**To get API keys:**

1. **FEC API Key** (Political Contributions):
   - Visit: https://api.open.fec.gov/developers/
   - Register for a free account
   - Request an API key
   - Wait for approval (usually 24-48 hours)

2. **ProPublica API Key** (Charitable Grants):
   - Visit: https://www.propublica.org/datastore/api
   - Register for a free account
   - Request API access
   - Receive API key via email

3. **SEC-API.io Key** (Financial Data):
   - Visit: https://sec-api.io/
   - Sign up for a free account
   - Get API key from dashboard
   - Free tier: 100 requests/month

### Setting Up Your .env File

1. **Copy the example file**:
   ```bash
   copy env_example.txt .env
   ```

2. **Choose your database configuration**:
   - **SQLite** (easiest): Uncomment `USE_SQLITE=true` and comment out PostgreSQL settings
   - **Local PostgreSQL**: Use the default settings in OPTION 1
   - **Remote database**: Use OPTION 3 or 4 and update with your connection details

3. **Add API keys** (optional):
   ```bash
   # Replace these placeholder values with your actual API keys
   FEC_API_KEY=abc123def456ghi789
   PROPUBLICA_API_KEY=xyz789abc123def456
   SEC_API_KEY=def456ghi789abc123
   ```

4. **Test your setup**:
   ```bash
   python manage.py test_ingestion
   ```

### Example .env File

Here's what your `.env` file should look like with real API keys:

```bash
# Database Configuration
DB_NAME=corp_spend_tracker
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
USE_SQLITE=false

# Django Configuration
SECRET_KEY=django-insecure-r55(7n1p8aad8d!)u_&6-4@!glt!ba!o93#%gajl(^8h^r9f#a
DEBUG=True

# API Keys (replace with your actual keys)
FEC_API_KEY=abc123def456ghi789
PROPUBLICA_API_KEY=xyz789abc123def456
SEC_API_KEY=def456ghi789abc123
```

### Using the Setup Script

For an interactive setup experience, run:

```bash
python setup_env.py
```

This script will guide you through:
- Database configuration
- API key setup
- Environment file creation

### Verifying API Key Status

Check if your API keys are working:

```bash
python manage.py test_ingestion
```

You'll see output like:
```
📋 API Key Status:
   FEC API: ✅ Configured
   ProPublica API: ✅ Configured
   SEC-API.io: ✅ Configured
   Senate LDA: ✅ Public data (no key required)
```

### Running with Real Data

Once you have API keys configured:

```bash
# Test with real data (dry run)
python manage.py ingest_data --dry-run

# Run real data ingestion
python manage.py ingest_data
```

## Development Setup

### Prerequisites
- Python 3.13+
- PostgreSQL (optional - can use SQLite for development)
- Git

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd corp-spend-tracking-politics
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
```

3. **Install backend dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

4. **Set up environment variables**:
   ```bash
   # Copy the example file and edit as needed
   copy env_example.txt .env
   ```

**Environment Configuration Options**:

**Option A: Local PostgreSQL (Recommended)**
```bash
# In .env file:
DB_NAME=corp_spend_tracker
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
USE_SQLITE=false
```

**Option B: SQLite (Easiest for development)**
```bash
# In .env file:
USE_SQLITE=true
# Other database settings will be ignored
```

**Option C: Remote PostgreSQL**
```bash
# In .env file:
DB_HOST=jwst.domain.castle
DB_USER=postgres
DB_PASSWORD=your_remote_password
USE_SQLITE=false
```

5. **Set up database**:
```bash
# For PostgreSQL:
python setup_postgres.py

# For SQLite (no setup needed):
# Just run migrations
python manage.py migrate
```

6. **Run migrations**:
```bash
python manage.py migrate
```

7. **Create superuser (optional)**:
```bash
python manage.py createsuperuser
```

8. **Create sample data (recommended for testing)**:
```bash
python manage.py create_sample_data
```

9. **Test the setup**:
```bash
python manage.py test data_collection
python manage.py test_ingestion
```

### Running the Application

#### Option 1: Quick Start (Windows)
Double-click one of these files to start both servers automatically:
- `start_dev.bat` (Command Prompt)
- `start_dev.ps1` (PowerShell)

#### Option 2: Manual Start

1. **Start the backend server**:
```bash
cd backend
python manage.py runserver
```

2. **Start the frontend server** (in a new terminal):
```bash
cd frontend
python server.py
```

3. **Open your browser** and navigate to:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Admin Panel: http://localhost:8000/admin/

## Data Ingestion Pipeline

The application collects data from multiple government sources:

### **Data Sources:**
- **FEC API**: Political contributions (requires API key)
- **Senate LDA**: Lobbying expenditures (public data)
- **IRS/ProPublica**: Charitable grants (requires API key)
- **SEC EDGAR**: Financial data (requires API key)

### **Key Features:**
- **Company Linking**: Automatically matches companies across datasets
- **Grant Classification**: Categorizes charitable grants (Religious, Education, Healthcare, etc.)
- **Data Quality Monitoring**: Tracks completeness and quality metrics
- **Dry Run Mode**: Test without saving data
- **Mock Data Fallback**: Works without API keys using sample data

### **Quick Start for Data Ingestion:**

1. **Get API keys** (optional for development):
   - FEC: https://api.open.fec.gov/developers/
   - ProPublica: https://www.propublica.org/datastore/api
   - SEC-API: https://sec-api.io/

2. **Configure** in `.env` file:
```
FEC_API_KEY=your_key_here
PROPUBLICA_API_KEY=your_key_here
SEC_API_KEY=your_key_here
```

3. **Test & Run**:
```bash
# Test the ingestion pipeline (uses mock data if no API keys)
python manage.py test_ingestion

# Run with sample data
python manage.py create_sample_data

# Run real data ingestion (if you have API keys)
python manage.py ingest_data --dry-run
python manage.py ingest_data
```

## API Endpoints

The application provides comprehensive REST API endpoints with advanced filtering, search, and analytics:

### **Core Endpoints:**
- `GET /api/companies/` - List companies with filtering and search
- `GET /api/companies/{id}/` - Get detailed company information
- `GET /api/companies/{id}/spending_summary/` - Get comprehensive spending analysis
- `GET /api/companies/top_spenders/` - Get top spending companies
- `GET /api/companies/search/` - Advanced company search

### **Analytics Endpoints:**
- `GET /api/financial-summaries/financial_ratios/` - Calculate financial ratios
- `GET /api/lobbying-reports/spending_trends/` - Lobbying spending trends
- `GET /api/lobbying-reports/top_issues/` - Most lobbied issues
- `GET /api/political-contributions/contribution_trends/` - Political contribution trends
- `GET /api/political-contributions/party_breakdown/` - Contributions by party
- `GET /api/charitable-grants/category_breakdown/` - Grants by category
- `GET /api/charitable-grants/grant_trends/` - Grant spending trends

### **Features:**
- **Filtering**: Filter by any model field
- **Search**: Full-text search across relevant fields
- **Pagination**: Automatic pagination with customizable page sizes
- **Sorting**: Sort by any field (ascending/descending)
- **Analytics**: Built-in aggregation and trend analysis

📖 **For complete API documentation, see [backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md)**

## Troubleshooting

### Common Issues

**Database Connection Errors:**
- If PostgreSQL is not available, set `USE_SQLITE=true` in your `.env` file
- For local PostgreSQL, ensure the service is running and credentials are correct
- For remote PostgreSQL, check network connectivity and credentials

**API Key Errors:**
- The application works with sample data even without API keys
- API keys are optional for development and testing
- Real data ingestion requires valid API keys from the respective services

**Import Errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` to install all dependencies
- Check that `django-filter` is installed (it was added to requirements.txt)

**Frontend Connection Issues:**
- Ensure backend server is running on port 8000
- Check CORS settings if accessing from different domains
- Use the Python HTTP server (`python server.py`) instead of opening files directly

## Project Status

✅ **Completed**: 
- Technology stack finalized
- Development environment set up
- Django models implemented
- Data ingestion pipeline built with mock data fallback
- REST API endpoints with advanced features
- Frontend interface with Alpine.js and Tailwind CSS
- Comprehensive testing and documentation

🔄 **In Progress**: 
- Data visualization and analytics
- Real data ingestion with API keys

⏳ **Pending**: 
- Advanced features
- Production deployment
- Performance optimization

## Recent Updates

- **Fixed**: Added missing `django-filter` dependency
- **Fixed**: Updated database configuration to support local development
- **Fixed**: Added mock data fallback for all data sources
- **Fixed**: Improved error handling in ingestion pipeline
- **Fixed**: Updated environment configuration template
- **Added**: SQLite support for easier development setup
