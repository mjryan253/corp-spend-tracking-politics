Of course. Here is the complete, consolidated project plan with all the updated information and task steps integrated into a single roadmap.

***

### ## Part 1: The Complete Data Collection Strategy

This project will synthesize data from four distinct sources to create a comprehensive profile of a company's influence and community spending.

* **Lobbying Expenditures 🏛️**
    * **Source:** The **U.S. Senate Lobbying Disclosure Act (LDA) Database**.
    * **Key Document:** Quarterly **LD-2 Reports**, which detail spending amounts and the specific issues lobbied on.
    * **Access Method:** Bulk XML downloads from the Senate LDA website.

* **Political Contributions 🗳️**
    * **Source:** The **Federal Election Commission (FEC)**.
    * **Details Tracked:** Campaign contributions from corporate Political Action Committees (PACs) to candidates and committees.
    * **Access Method:** The official **FEC Developer API**.

* **Charitable & Religious Spending 🙏**
    * **Source:** The **IRS Database of Tax-Exempt Organizations**.
    * **Key Document:** **Form 990-PF**, the annual tax return filed by private foundations, including corporate foundations. This form publicly lists every grant made.
    * **Access Method:** APIs like **ProPublica's Nonprofit Explorer** or bulk data downloads from the IRS on AWS.

* **Corporate Financial Context 💰**
    * **Source:** **SEC EDGAR**, initially accessed via the **SEC-API.io** service.
    * **Purpose:** To retrieve top-line financial figures like **total revenue** and **net income**. This provides the essential context for calculating spending as a percentage of the company's total financial activity.
    * **Design Note:** The data ingestion script will be built with a modular wrapper for this API, allowing for a future switch to direct EDGAR parsing without a major rewrite.

***

### ## Part 2: The Complete PostgreSQL Database Schema

This schema is designed to store all the data from the sources above in a structured, relational way. In Django, these will be implemented as `models`.

* **`companies` Table:** The central table for company information.
    * `id`: Primary Key
    * `name`, `ticker`, `cik`, `headquarters_location`

* **`financial_summaries` Table:** Stores contextual financial data.
    * `id`: Primary Key
    * `company_id`: Foreign Key to `companies`
    * `fiscal_year`, `total_revenue`, `net_income`

* **`lobbying_reports` Table:** Stores lobbying data from Senate filings.
    * `id`: Primary Key
    * `company_id`: Foreign Key to `companies`
    * `year`, `quarter`, `amount_spent`, `specific_issues`, `report_url`

* **`political_contributions` Table:** Stores campaign contribution data from the FEC.
    * `id`: Primary Key
    * `company_pac_id`: A text field for the PAC's name or a foreign key to a dedicated PACs table.
    * `recipient_name`, `recipient_party`, `amount`, `date`, `election_cycle`

* **`charitable_grants` Table:** Stores grant data from IRS Form 990-PF.
    * `id`: Primary Key
    * `company_id`: Foreign Key to `companies`
    * `recipient_name`, `recipient_ein` (EIN of the nonprofit)
    * `amount`, `fiscal_year`, `grant_description`
    * `recipient_category`: A field you will populate (e.g., "Religious," "Education," "Healthcare").

***

### ## Part 3: The Complete Web App Development Task List

This is the step-by-step plan for you and your agent to build, test, and deploy the application.

#### **Phase 1: Foundation and Data Backend**

* **✅ Task 1: Finalize Technology Stack.**
    * **Backend:** Python with **Django** and **Django REST Framework (DRF)**.
    * **Database:** **PostgreSQL**.
    * **Frontend:** **HTML, CSS, and JavaScript**.

* **✅ Task 2: Set Up Development Environment.**
    * Install Python, Django, DRF, and the PostgreSQL adapter (`psycopg2-binary`).
    * Initialize a Django project and a Git repository for version control.

* **✅ Task 3: Implement Schema in Django Models.**
    * Define the tables from Part 2 as Python classes in your `models.py` file.
    * Use Django's `migrate` command to create the tables in your PostgreSQL database.

* **✅ Task 4: Build the Modular Data Ingestion Pipeline.**
    * Create a Django management command to run your data collection script.
    * **Step A:** Write modules to fetch data from the **FEC API**, **Senate LDA downloads**, and **IRS 990 data**.
    * **Step B:** Write a separate, swappable module to fetch financial context from **SEC-API.io**.
    * **Step C:** Develop your **classification logic** for charitable grants, using keywords to identify and tag religious organizations in the `recipient_category` field.
    * **Step D:** Write the core logic to clean, link (e.g., match a company name across different datasets), and save all data into your Django models.

---

#### **Phase 2: Building the Web Application**

* **✅ Task 5: Auto-Generate Backend API Endpoints with DRF.**
    * For each model (Company, Grant, etc.), create a **Serializer** class to define its JSON representation.
    * For each model, create a **ViewSet** class. Using DRF's `ModelViewSet` will automatically generate a full suite of RESTful API endpoints (GET, POST, etc.) for each data type.

* **✅ Task 6: Design and Build the Frontend User Interface.**
    * Create the core HTML and CSS files for the search page (`index.html`) and the detailed company results page (`company.html`). Focus on a clean, readable, and mobile-friendly design.

* **✅ Task 7: Connect Frontend to Backend.**
    * Write JavaScript code using the `fetch()` API. This code will call your DRF endpoints based on user searches, retrieve the data, and dynamically populate the HTML on the results page.

---

#### **Phase 3: Refinement and Deployment**

* **✅ Task 8: Implement Data Visualization.**
    * Use a JavaScript library like **Chart.js** to create visual representations of the data on the company page.
    * **Lobbying:** A time-series chart of spending over the last several quarters.
    * **Political:** A pie chart showing the breakdown of contributions by political party. 
    * **Charitable:** A donut chart showing the breakdown of giving by category (Religious, Education, etc.).

* **✅ Task 9: Add User Experience Features.**
    * Implement loading indicators for API calls and clear error messages for failed searches.
    * Refine search functionality and consider adding filters (e.g., by year).

* **✅ Task 10: Testing.**
    * Thoroughly test the application, paying close attention to the accuracy of the data being displayed. Check for bugs across different web browsers.

* **✅ Task 11: Deployment.**
    * Choose a cloud platform (like **Heroku**, **AWS**, or **DigitalOcean**) to deploy your Django application and PostgreSQL database, making it live on the web.