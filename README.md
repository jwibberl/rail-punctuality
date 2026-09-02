# Train Punctuality

A Python/Flask application that retrieves historical train performance data from the Rail Data Marketplace Historical Service Performance (HSP) API, stores the results in PostgreSQL, and provides train punctuality visualisations through Grafana.

This project was developed as a practical data engineering project, combining API integration, data ingestion, relational database design, SQL analysis, and data visualisation.

## Overview

The application allows a user to specify:

* Origin station
* Destination station
* Date range
* Time range
* Weekday or weekend services

The application then retrieves historical service performance data from the Rail Data Marketplace Historical Service Performance (HSP) API.

The returned data is processed by Python and stored in a PostgreSQL database.

Grafana connects to the PostgreSQL database to provide visualisations of train punctuality and allow performance to be compared between stations.

## Architecture

```text
                     ┌──────────────────┐
                     │   Web Interface  │
                     │     (Flask)      │
                     └────────┬─────────┘
                              │
                              │ Request
                              ▼
                     ┌──────────────────┐
                     │     HSP API      │
                     │  Rail Data       │
                     │  Marketplace     │
                     └────────┬─────────┘
                              │
                              │ JSON
                              ▼
                     ┌──────────────────┐
                     │ Python Data      │
                     │ Processing       │
                     └────────┬─────────┘
                              │
                              │ Insert
                              ▼
                     ┌──────────────────┐
                     │   PostgreSQL     │
                     │    Database      │
                     └────────┬─────────┘
                              │
                              │ SQL
                              ▼
                     ┌──────────────────┐
                     │     Grafana      │
                     │  Visualisation   │
                     └──────────────────┘
```

## Technologies

* Python
* Flask
* PostgreSQL
* psycopg2
* Requests
* python-dotenv
* Grafana
* HTML/CSS
* SQL
* Git/GitHub
* Rail Data Marketplace Historical Service Performance API

## Project Structure

```text
train-punctuality/
│
├── train-punctuality.py    # Flask application and HSP API integration
├── db.py                   # PostgreSQL connection and database operations
├── station.py              # Station data processing
├── service.py              # Service and service-run processing
├── arrivals.py             # Arrival data processing
├── graph.py                # Punctuality graph generation
│
├── templates/
│   └── index.html          # Web interface
│
├── .env                    # Local configuration and API credentials
├── .gitignore              # Files excluded from Git
└── README.md               # Project documentation
```

## Data Pipeline

The application follows an ETL-style workflow.

### 1. Extract

The Flask application collects the parameters entered by the user and sends a request to the Historical Service Performance API.

The request includes:

* Origin location
* Destination location
* Start time
* End time
* Start date
* End date
* Weekday or weekend selection

The API returns historical service performance data in JSON format.

### 2. Transform

The returned JSON data is processed by the Python application.

The data is separated into the appropriate entities:

* Stations
* Services
* Service runs
* Arrivals

The individual Python modules are responsible for processing and storing the different types of data.

### 3. Load

The processed data is loaded into PostgreSQL.

The database provides a structured relational dataset that can then be queried for analysis and visualisation.

## Database

The PostgreSQL database separates train service information into related tables.

The main entities are:

```text
station
   │
   └── service
          │
          └── service_run
                  │
                  └── arrival
```

This structure allows individual arrivals to be associated with a specific service run, while services and stations can be maintained as separate entities.

The relational design also allows SQL queries to analyse punctuality across multiple stations and services.

## Punctuality Analysis

The project uses arrival delay information to analyse train punctuality.

The current analysis uses tolerance thresholds of:

```text
< 1 minute
< 2 minutes
< 5 minutes
```

These thresholds allow the number of arrivals meeting each punctuality category to be compared between stations.

For example, Grafana can be used to produce a bar chart showing the number of arrivals within each punctuality threshold for each station.

## Grafana

Grafana is connected directly to the PostgreSQL database using the PostgreSQL data source.

SQL queries are used to retrieve punctuality data from the database.

The resulting data can be visualised using Grafana dashboards, allowing train performance to be compared between stations.

Current analysis includes:

* Number of arrivals within one minute
* Number of arrivals within two minutes
* Number of arrivals within five minutes
* Comparison of punctuality between stations
* Visualisation of arrival performance using bar charts

Using Grafana allows the data stored by the Python application to be analysed without requiring the visualisation logic to be built into the Flask application itself.

## Configuration

The application uses environment variables for database credentials and the API key.

Create a `.env` file containing:

```text
POSTGRES_HOST=your_database_host
POSTGRES_USER=your_database_user
POSTGRES_DB=your_database_name
POSTGRES_PASSWORD=your_database_password
API_KEY=your_api_key
```

The `.env` file contains sensitive configuration information and should **not** be committed to GitHub.

It should be included in `.gitignore`:

```text
.env
```
The database you configure in these variables needs to exist, the username and password must work with the database server.
A subscription to the Historical Services Platform (HSP) API is needed, which is currently free. More information is at: https://wiki.openraildata.com/index.php/HSP
You need to provide your API key.

## Running the Application

Clone the repository:

```bash
git clone https://github.com/jwibberl/train-punctuality.git
cd train-punctuality
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install the required Python packages:

```bash
pip install flask requests psycopg2-binary python-dotenv markupsafe
```

Configure the PostgreSQL database and create the `.env` file with the required credentials and API key.

The application can then be started with:

```bash
python train-punctuality.py
```

The Flask development server will provide the web interface.

## API

The project uses the Rail Data Marketplace Historical Service Performance (HSP) API.

The API provides historical performance information for train services.

The application sends a POST request containing the required journey and date/time parameters and receives service performance data in JSON format.

The returned data is then processed and stored in PostgreSQL for further analysis.

## Application Workflow

The basic application workflow is:

```text
User enters journey criteria
            │
            ▼
       Flask application
            │
            ▼
      HSP API request
            │
            ▼
     Historical service data
            │
            ▼
      Python processing
            │
            ▼
        PostgreSQL
            │
            ▼
         SQL queries
            │
            ▼
         Grafana
            │
            ▼
    Punctuality visualisation
```

## Purpose

This project was developed as a practical demonstration of data engineering concepts using a real-world transport dataset.

It demonstrates experience with:

* Consuming a REST API
* Working with JSON data
* Processing data using Python
* Designing a relational database
* Writing SQL queries
* Loading data into PostgreSQL
* Developing a Flask web application
* Creating data visualisations with Grafana
* Managing configuration using environment variables
* Using Git and GitHub

## What I Learned

The project provided practical experience in building a small end-to-end data pipeline rather than working with an isolated dataset.

Particular areas of experience include:

* Integrating an external API into a Python application
* Understanding and processing API data
* Designing relationships between stations, services, service runs and arrivals
* Managing PostgreSQL connections from Python
* Separating application functionality into multiple Python modules
* Using SQL to transform database data into useful metrics
* Connecting Grafana directly to PostgreSQL
* Debugging API, database and application integration issues
* Using Git for version control throughout development

## Future Improvements

Potential improvements to the project include:

* Make the web UI nicer, add well-designed CSS
* Automated scheduled data collection
* Additional punctuality thresholds
* Historical punctuality trends
* Analysis by individual train service
* Analysis by operator
* Additional Grafana dashboards
* Improved API and database error handling
* Automated unit and integration testing
* Database indexing and query optimisation
* Containerisation using Docker
* Automated deployment

## Author

**James Wibberley**

Technical professional with over 20 years of experience across software development, Linux administration, cloud infrastructure and technical support, with recent hands-on experience in data engineering.

GitHub: https://github.com/jwibberl
