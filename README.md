# Expense Tracker

A simple FastAPI-based expense management application built for the machine test. It supports expense CRUD operations, filtering by time/category, and a totals summary endpoint backed by SQLite.

## Features

- Create, list, update, and delete expenses
- Filter expenses by `year`, `month`, `week`, `day`, and `category`
- Get monthly expenses from a dedicated endpoint
- Get `total_expense`, `total_salary`, and `remaining_amount`
- Automatic Swagger docs via FastAPI

## Project Structure

```text
expense_tracker/
  app/
    main.py
    database.py
    models.py
    schemas.py
    expenses.db
```

## Requirements

- Python 3.12+

## Installation

```bash
pip install -r requirements.txt
```

## Run The API

From the `expense_tracker` directory:

```bash
uvicorn app.main:app --reload
```

Open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Configuration

You can set a salary value for the totals endpoint using the `TOTAL_SALARY` environment variable.

Windows PowerShell:

```powershell
$env:TOTAL_SALARY="50000"
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /expenses/` - Create a new expense
- `GET /expenses/` - List expenses with optional filters
- `GET /expenses/{expense_id}` - Get a single expense
- `PUT /expenses/{expense_id}` - Update an expense
- `DELETE /expenses/{expense_id}` - Delete an expense
- `GET /expenses/month/{year}/{month}/` - Get expenses for a month
- `GET /totals/` - Get total expenses, configured salary, and remaining amount

## Example Filter Request

```text
GET /expenses/?year=2026&month=4&category=food
```

## Notes

- SQLite is used as the database.
- Expense responses expose `expense_id` in the API response.
- The current database file already includes seeded sample data.
