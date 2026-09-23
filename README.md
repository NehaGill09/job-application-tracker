# Job Application Tracker Pro

A professional desktop job-search management application built with Python, Tkinter, and SQLite.

## Features

- Dashboard with pipeline statistics
- Company and role tracking
- Application pipeline: Saved -> Applied -> Screening -> Interview -> Offer / Rejected
- Search across company, role, location, contact, and notes
- Status filtering
- Application, deadline, and interview dates
- Upcoming and overdue attention indicators
- Salary range tracking
- Open job links directly from the app
- Contacts and notes
- Edit and delete applications
- CSV and Excel export
- PDF and JSON reporting modules
- SQLite persistence
- Automated tests
- Personal database files excluded from Git

## Requirements

- Python 3.10+
- Tkinter (usually included with Python; Linux may require python3-tk)

## Run

macOS / Linux:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python main.py

Windows:

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python main.py

## Test

    python -m pytest

## Data and exports

The app creates job_tracker.db locally. It is intentionally ignored by Git.

The reporting module supports CSV, Excel, PDF, and JSON output.

## Project structure

    main.py
    app/
      database.py
      models.py
      services.py
      reports.py
      ui.py
    tests/
      test_database.py
      test_services.py
    requirements.txt
    .gitignore

## Validation

Dates use YYYY-MM-DD. Salary fields accept values such as 65000 or 65,000.

This project demonstrates Python desktop UI development, SQLite data modeling, validation, reporting, file export, and automated testing.
