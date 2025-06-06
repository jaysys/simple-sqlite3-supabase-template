# SQLite3 to Supabase PostgreSQL Migration Tool

A Python-based toolkit for managing and migrating data between SQLite3 and Supabase PostgreSQL databases. This project provides utilities for database inspection, data migration, and query execution.

## Features

- **Database Inspection**: View tables, views, and their schemas
- **Data Migration**: Migrate data from SQLite3 to Supabase PostgreSQL
- **Query Execution**: Execute custom SQL queries with flexible result handling
- **Environment-based Configuration**: Secure database credentials management using `.env` files

## Prerequisites

- Python 3.7+
- SQLite3
- Supabase PostgreSQL database
- Required Python packages (install via `pip install -r requirements.txt`):
  - sqlalchemy
  - psycopg2-binary
  - python-dotenv

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your database URL:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

## Usage

### Database Inspection

View database schema including tables and views:

```python
from main import get_table_info

get_table_info()
```

### Executing Queries

#### Fetch one, many, and all results:
```python
from main import fetch_one_many_all_from_exec_query

query = "SELECT * FROM your_table"
one, many, all_results = fetch_one_many_all_from_exec_query(query)
```

#### Fetch all results:
```python
from main import fetch_all_from_exec_query

query = "SELECT * FROM your_table"
results = fetch_all_from_exec_query(query)
```

### Example Use Cases

1. **Basic Query Execution**:
   ```python
   # In use_case_01()
   query = """
   SELECT * 
   FROM asset_total_history_report 
   ORDER BY "timestamp"
   """
   data = fetch_one_many_all_from_exec_query(query)
   ```

2. **Count Records**:
   ```python
   # In use_case_02()
   count_query = "SELECT count(*) FROM asset_total_history_report"
   count = fetch_all_from_exec_query(count_query)
   ```

## Project Structure

- `main.py`: Core functionality for database operations and inspection
- `migration-sqlite3-to-supa.py`: SQLite3 to Supabase PostgreSQL migration script
- `dashboard-with-supa.py`: Streamlit-based dashboard for data visualization
- `.env`: Environment configuration (not version controlled)
- `requirements.txt`: Python dependencies

## Security Note

- Never commit sensitive information like database credentials to version control
- The `.env` file is included in `.gitignore` by default
- Use environment variables for all sensitive configuration

## License

[MIT](LICENSE)
