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
   - Install PostgreSQL
   - Create database: `corp_spend_tracker`
   - Update database credentials in `corp_spend_tracker/settings.py`

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

## Database Schema

The application uses the following main models:
- **Company**: Central company information
- **FinancialSummary**: Annual financial data
- **LobbyingReport**: Quarterly lobbying expenditures
- **PoliticalContribution**: Campaign contributions
- **CharitableGrant**: Foundation grants and donations

## Next Steps

- [ ] Set up PostgreSQL database
- [ ] Implement data ingestion pipeline
- [ ] Build REST API endpoints
- [ ] Create frontend interface
- [ ] Add data visualization
- [ ] Deploy to production

## Project Status

✅ **Completed**: Tasks 1-2 (Technology stack finalized, development environment set up)
🔄 **In Progress**: Task 3 (Django models implemented, ready for database setup)
⏳ **Pending**: Tasks 4-11 (Data ingestion, API, frontend, deployment)
