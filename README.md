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
- **Database**: PostgreSQL (required)
- **Frontend**: HTML, CSS, and JavaScript

## Development Setup

### Prerequisites
- Python 3.13+
- PostgreSQL
- Git

### Installation

**⚠️ Important**: This application requires PostgreSQL. SQLite is not supported.

1. Clone the repository:
```bash
git clone <repository-url>
cd corp-spend-tracking-politics
```

2. Create and activate virtual environment:
```bash
py -3 -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
```

3. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
   - Download and install PostgreSQL from https://www.postgresql.org/download/windows/
   - Use default settings during installation
   - Set password for 'postgres' user to 'postgres'
   - Run the setup script: `python setup_postgres.py` or double-click `setup_postgres.bat`
   - Configure your database credentials in the `.env` file

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser (optional):
```bash
python manage.py createsuperuser
```

7. Create sample data (optional):
```bash
python manage.py create_sample_data
```

8. Run tests:
```bash
python manage.py test data_collection
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

## Database Schema

The application uses PostgreSQL with the following main models:
- **Company**: Central company information
- **FinancialSummary**: Annual financial data
- **LobbyingReport**: Quarterly lobbying expenditures
- **PoliticalContribution**: Campaign contributions
- **CharitableGrant**: Foundation grants and donations

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

📖 **For complete API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

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

### **Quick Start:**

1. **Get API keys** from:
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
python manage.py test_ingestion
python manage.py ingest_data --dry-run
python manage.py ingest_data
```

📖 **For detailed configuration, see [in-depth-configuration.md](in-depth-configuration.md)**

## Next Steps

- [x] Set up PostgreSQL database
- [x] Implement data ingestion pipeline
- [x] Build REST API endpoints with advanced features
- [x] Create frontend interface with Alpine.js and Tailwind CSS
- [ ] Add data visualization and analytics
- [ ] Deploy to production

## Project Status

✅ **Completed**: Tasks 1-6 (Technology stack finalized, development environment set up, Django models implemented, data ingestion pipeline built, REST API endpoints with advanced features, frontend interface with Alpine.js and Tailwind CSS)
🔄 **In Progress**: Task 7 (Data visualization and analytics)
⏳ **Pending**: Tasks 8-11 (Advanced features, deployment, optimization)
