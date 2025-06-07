# Supabase PostgreSQL Performance Benchmark

A Python tool for comparing query performance between SQLAlchemy and Supabase client when working with Supabase PostgreSQL databases. This project helps you understand the performance characteristics of different database access methods.

## Features

- **Database Inspection**: View tables, views, and their schemas
- **Performance Benchmarking**: Compare SQLAlchemy vs Supabase client performance
- **Query Execution**: Execute custom SQL queries with flexible result handling
- **Environment-based Configuration**: Secure database credentials management using `.env` files

## Prerequisites

- Python 3.7+
- SQLite3
- Supabase PostgreSQL database
- Required Python packages (see `requirements.txt`)

## Project Structure

```
.
├── .env                    # Environment variables
├── .env-sample             # Example environment variables
├── main.py                 # Main application code
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd simple-sqlite3-supabase-template
   ```

2. **Create and activate virtual environment**

   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows:
   # .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Copy `.env-sample` to `.env` and update with your Supabase credentials:
   ```bash
   cp .env-sample .env
   # Edit .env with your credentials
   ```
   Required environment variables:
   ```
   DATABASE_URL=postgresql://postgres.user:password@host:port/database
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   ```

## Usage

### Running the Benchmark

The benchmark compares the performance of SQLAlchemy and Supabase client when querying your database:

```bash
python main.py
```

This will:

1. Test both `asset_master` and `asset_total_history_report` tables
2. Show execution times for both SQLAlchemy and Supabase client
3. Display performance comparison

### Example Output

```
# Actual benchmark runs
sqlalchemy_result = benchmark_sqlalchemy_query(table, limit=9_900_000)
supabase_result = benchmark_supabase_query(table, limit=9_900_000) # supabase client 를 이용하면 아무리 큰 limit 를 주더라도 1000개까지만 가져옴. 따라서 주의해야한다. 제대로 비교할려면 양 쪽 케이스 모두를 1000으로 설정해야한다.
results.extend([sqlalchemy_result, supabase_result])

=-=-=-=-=-=-=-=-=-=- start!

asset_master rows 1
asset_master rows 1
asset_master rows 2017612
asset_master rows 1000  <== limit
=== asset_master Benchmark Results ===
SQLAlchemy: 8.19 seconds
Supabase:   0.19 seconds
Supabase is 4187.01% faster

asset_total_history_report rows 1
asset_total_history_report rows 1
asset_total_history_report rows 88393
asset_total_history_report rows 1000  <== limit
=== asset_total_history_report Benchmark Results ===
SQLAlchemy: 0.82 seconds
Supabase:   0.75 seconds
Supabase is 9.10% faster

=-=-=-=-=-=-=-=-=-=- done!
```

### Database Inspection

View database schema including tables and views:

```python
from main import get_table_info

get_table_info()
```

### Query Execution

Execute custom SQL queries and fetch results in different ways:

```python
from main import fetch_one_many_all_from_exec_query

# Example query
query = "SELECT * FROM asset_master LIMIT 10"
one, many, all_results = fetch_one_many_all_from_exec_query(query)

# one: First row
# many: Next 2 rows
# all_results: All remaining rows
```

## Important Notes

1. **Supabase Client Limitation**: The Supabase client limits results to 1000 rows by default, even if a larger limit is specified.
2. **Connection Handling**: The benchmark includes connection setup time. For production use, consider connection pooling.
3. **Warm-up**: The first query might be slower due to connection establishment.

## Dependencies

- SQLAlchemy >= 2.0.0
- psycopg2-binary >= 2.9.9
- python-dotenv >= 1.0.0
- supabase >= 2.0.0

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
