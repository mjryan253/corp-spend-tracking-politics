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
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, and JavaScript

## Development Setup

### Prerequisites
- Python 3.13+
- PostgreSQL (for production)
- Git

### Installation

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

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
   - Download and install PostgreSQL from https://www.postgresql.org/download/windows/
   - Use default settings during installation
   - Set password for 'postgres' user to 'postgres'
   - Run the setup script: `python setup_postgres.py` or double-click `setup_postgres.bat`

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser (optional):
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

8. Create sample data (optional):
```bash
python manage.py create_sample_data
```

9. Run tests:
```bash
python manage.py test data_collection
```

## Database Schema

The application uses the following main models:
- **Company**: Central company information
- **FinancialSummary**: Annual financial data
- **LobbyingReport**: Quarterly lobbying expenditures
- **PoliticalContribution**: Campaign contributions
- **CharitableGrant**: Foundation grants and donations

## API Endpoints

The application provides REST API endpoints for all models:

- `GET /api/companies/` - List all companies
- `GET /api/companies/{id}/` - Get detailed company information with related data
- `GET /api/companies/{id}/spending_summary/` - Get spending summary for a company
- `GET /api/financial-summaries/` - List financial summaries
- `GET /api/lobbying-reports/` - List lobbying reports
- `GET /api/political-contributions/` - List political contributions
- `GET /api/charitable-grants/` - List charitable grants

All endpoints support standard REST operations (GET, POST, PUT, DELETE).

## Data Ingestion Pipeline

The application includes a modular data ingestion pipeline that collects data from multiple government sources:

### **Data Sources:**
- **FEC API**: Political contributions from corporate PACs
- **Senate LDA**: Lobbying expenditures and reports
- **IRS/ProPublica**: Charitable grants and foundation data
- **SEC EDGAR**: Financial data and company information

### **Features:**
- **Modular Design**: Each data source has its own ingestion module
- **Company Linking**: Automatically links companies across different datasets
- **Classification System**: Categorizes charitable grants (Religious, Education, Healthcare, etc.)
- **Data Quality Reporting**: Monitors data completeness and quality
- **Dry Run Mode**: Test data ingestion without saving to database

### **Usage:**

1. **Set up API keys** in your `.env` file:
```
FEC_API_KEY=your_fec_api_key_here
PROPUBLICA_API_KEY=your_propublica_api_key_here
SEC_API_KEY=your_sec_api_key_here
```

2. **Test the pipeline**:
```bash
python manage.py test_ingestion
```

3. **Run data ingestion**:
```bash
# Dry run (no data saved)
python manage.py ingest_data --dry-run

# Full ingestion
python manage.py ingest_data

# Specific sources only
python manage.py ingest_data --sources fec lobbying

# Specific year
python manage.py ingest_data --year 2023
```

## Next Steps

- [x] Set up PostgreSQL database
- [x] Implement data ingestion pipeline
- [ ] Build REST API endpoints
- [ ] Create frontend interface
- [ ] Add data visualization
- [ ] Deploy to production

## Project Status

✅ **Completed**: Tasks 1-4 (Technology stack finalized, development environment set up, Django models implemented, data ingestion pipeline built)
🔄 **In Progress**: Task 5 (REST API endpoints)
⏳ **Pending**: Tasks 6-11 (Frontend interface, data visualization, deployment)
