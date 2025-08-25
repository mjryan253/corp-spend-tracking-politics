
# Corporate Spending Tracker

A comprehensive web application that tracks and analyzes corporate spending across lobbying, political contributions, and charitable giving by synthesizing data from multiple U.S. government sources.

## Project Overview

This application provides a transparent view of corporate influence by collecting, linking, and displaying data from:

  * **🏛️ Lobbying Expenditures**: U.S. Senate Lobbying Disclosure Act (LDA) Database.
  * **🗳️ Political Contributions**: Federal Election Commission (FEC).
  * **🙏 Charitable & Religious Spending**: IRS Database of Tax-Exempt Organizations.
  * **💰 Corporate Financial Context**: SEC EDGAR.

The backend is built with **Django** and **PostgreSQL**, providing a robust API, while the frontend is a lightweight, responsive interface built with **Alpine.js** and **Tailwind CSS**.

-----

## Getting Started (Docker)

The easiest and recommended way to run this application is with Docker.

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

-----

## Configuration

### In-Depth Configuration

 For a detailed guide on the containerized architecture, data source APIs, company linking system, and more, please refer to the **[In-Depth Configuration Guide](backend/in-depth-configuration.md)**.

### API Keys for Real Data

The application can run entirely with sample data out-of-the-box. To ingest real-time data from government sources, you will need to acquire free API keys and add them to your `.env` file.

  * **`FEC_API_KEY`**: For political contributions.
  * **`PROPUBLICA_API_KEY`**: For charitable grants.
  * **`SEC_API_KEY`**: For corporate financial data.

 For detailed instructions on obtaining and configuring these keys, see the **[In-Depth Configuration Guide](backend/in-depth-configuration.md)**.

-----

## Data Ingestion

The application features a powerful data ingestion pipeline to collect and process data. You can control it using Django management commands.

```bash
# Test the ingestion pipeline (uses mock data if no API keys are set)
docker-compose exec backend python manage.py test_ingestion

# Populate the database with initial sample data
docker-compose exec backend python manage.py create_sample_data

# Run the full data ingestion (requires API keys for real data)
docker-compose exec backend python manage.py ingest_data
```

-----

## API Documentation

 The backend provides a full-featured REST API with endpoints for companies, financials, lobbying, and more. For complete details, including all available filters and analytics endpoints, please see the **[API Documentation](backend/API_DOCUMENTATION.md)**.

-----

## Support the Project

This is an open-source project dedicated to increasing transparency in corporate spending. If you find it useful, please consider supporting its development. Your support helps cover server costs and allows for continued enhancements.

