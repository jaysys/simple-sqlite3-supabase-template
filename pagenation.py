import os
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.engine import CursorResult
from dotenv import load_dotenv
from dataclasses import dataclass
from rich import print

# Load environment variables from .env file
load_dotenv()
CONNECTION_STRING = os.getenv('DATABASE_URL')

if not CONNECTION_STRING:
    raise ValueError("DATABASE_URL environment variable not found")

# Create SQLAlchemy engine
engine = create_engine(CONNECTION_STRING)

@dataclass
class PaginationResult:
    """Pagination result container"""
    items: List[Dict[str, Any]]
    total: int
    page: int
    per_page: int
    total_pages: int


def get_table_info() -> None:
    """Print database schema information including tables and views"""
    meta = MetaData()
    meta.reflect(bind=engine, views=True)
    
    with engine.connect() as conn:
        # Get list of views
        view_query = text("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public';
        """)
        
        # Print tables
        print("\n=== Tables ===")
        for table_name in meta.tables:
            print(f"Table: {table_name}")
        
        # Print views
        print("\n=== Views ===")
        views = [row[0] for row in conn.execute(view_query)]
        if not views:
            print("No views found.")
        else:
            for view_name in views:
                print(f"View: {view_name}")


def get_table_schema(table_name: str) -> None:
    """Print schema information for a specific table or view"""
    inspector = MetaData()
    
    with engine.connect() as conn:
        # Check if table exists
        table_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = :table_name;
        """)
        
        # Check if view exists
        view_query = text("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' AND table_name = :view_name;
        """)
        
        table_exists = conn.execute(table_query, {"table_name": table_name}).fetchone()
        view_exists = conn.execute(view_query, {"view_name": table_name}).fetchone()
        
        if table_exists:
            print(f"\n=== Table '{table_name}' Schema ===")
            columns_query = text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = :table_name
                ORDER BY ordinal_position;
            """)
            columns = conn.execute(columns_query, {"table_name": table_name})
            for col in columns:
                print(f"{col[0]}: {col[1]}")
                
        elif view_exists:
            print(f"\n=== View '{table_name}' Schema ===")
            columns_query = text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = :view_name
                ORDER BY ordinal_position;
            """)
            columns = conn.execute(columns_query, {"view_name": table_name})
            for col in columns:
                print(f"{col[0]}: {col[1]}")
        else:
            print(f"\nTable or view '{table_name}' not found.")

def execute_query(query: str, params: Optional[Dict] = None) -> CursorResult:
    """Execute a raw SQL query and return the result"""
    with engine.connect() as conn:
        return conn.execute(text(query), params or {})


def fetch_one(query: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Fetch a single row from a query"""
    result = execute_query(query, params)
    row = result.fetchone()
    if not row:
        return None
    return dict(zip(result.keys(), row))


def fetch_all(query: str, params: Optional[Dict] = None) -> List[Dict]:
    """Fetch all rows from a query"""
    result = execute_query(query, params)
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


def fetch_one_many_all(query: str, params: Optional[Dict] = None) -> tuple:
    """
    Execute a query and return (one, many, all) results
    
    Args:
        query: SQL query string
        params: Optional query parameters
        
    Returns:
        tuple: (first_row, next_two_rows, remaining_rows)
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        first = result.fetchone()
        next_two = result.fetchmany(2)
        remaining = result.fetchall()
        return first, next_two, remaining


def paginate_query(
    query: str,
    page: int = 1,
    per_page: int = 100,
    params: Optional[Dict] = None,
    count_query: Optional[str] = None
) -> PaginationResult:
    """
    Execute a paginated query
    
    Args:
        query: Base SQL query (without LIMIT/OFFSET)
        page: Page number (1-based)
        per_page: Items per page
        params: Query parameters
        count_query: Optional custom count query. If not provided, 
                   will be generated from the base query
    
    Returns:
        PaginationResult object with items and pagination info
    """
    if page < 1:
        page = 1
    
    offset = (page - 1) * per_page
    
    # Add pagination to the query
    paginated_query = f"{query} LIMIT {per_page} OFFSET {offset}"
    
    # Execute the paginated query
    items = fetch_all(paginated_query, params)
    
    # Get total count
    if not count_query:
        # Simple count query generation (may not work for all SQL)
        count_query = f"SELECT COUNT(*) AS count FROM ({query}) AS subquery"
    
    total = fetch_one(count_query, params)['count']
    total_pages = (total + per_page - 1) // per_page
    
    return PaginationResult(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


def row_to_dict(row):
    """Convert SQLAlchemy row to dictionary"""
    if row is None:
        return None
    if hasattr(row, '_asdict'):  # For SQLAlchemy 1.4+
        return row._asdict()
    elif hasattr(row, '_mapping'):  # For SQLAlchemy 1.4+ with future=True
        return dict(row._mapping)
    return dict(row)  # Fallback


def example_queries() -> None:
    """Example queries demonstrating different ways to fetch data"""

    # Example 1: Using pagination
    print(" --> Example 1: Pagination")
    paginated = paginate_query(
        "SELECT * FROM asset_master ORDER BY timestamp DESC",
        page=3,
        per_page=20
    )
    print(f"Page {paginated.page} of {paginated.total_pages}")
    print(f"Showing {len(paginated.items)} of {paginated.total} items")
    print("First item:", row_to_dict(paginated.items[0]) if paginated.items else "No items")


    # Example 2: Fetch first row and next two rows
    query1 = """
    SELECT * 
    FROM asset_total_history_report 
    ORDER BY timestamp DESC
    LIMIT 1000  -- Added limit for safety
    """
    first, next_two, remaining = fetch_one_many_all(query1)
    
    print("\n --> Example 2: Fetching Rows")
    print("First row:")
    print(row_to_dict(first) if first else 'No data')
    print("Next two rows:")
    print([row_to_dict(row) for row in next_two])
    print("Total rows:", len(remaining) + len(next_two) + (1 if first else 0))
    

    # Example 3: Parameterized query
    print("\n --> Example 3: Parameterized Query")
    result = fetch_one(
        "SELECT * FROM asset_master WHERE asset_name = :asset_name ORDER BY timestamp DESC",
        params={"asset_name": "BTC"}
    )
    print("BTC details:", row_to_dict(result) if result else "Not found")


def benchmark_query(table_name: str, limit: int = 1000) -> Dict[str, Any]:
    """
    Execute a benchmark query and return timing information
    
    Args:
        table_name: Name of the table to query
        limit: Maximum number of rows to return
        
    Returns:
        Dict containing benchmark results
    """
    import time
    
    # Simple select query
    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    
    # Time the query
    start_time = time.time()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
    
    execution_time = time.time() - start_time
    
    return {
        'execution_time': execution_time,
        'rows_returned': len(rows),
        'table': table_name,
        'limit': limit,
        'rows_per_second': len(rows) / execution_time if execution_time > 0 else 0
    }


def run_benchmark(table_names: List[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Run benchmark queries on specified tables
    
    Args:
        table_names: List of table names to benchmark (default: ['asset_master', 'asset_total_history_report'])
        limit: Maximum number of rows to fetch in each query
        
    Returns:
        List of benchmark results
    """
    if table_names is None:
        table_names = ['asset_master', 'asset_total_history_report']
    
    results = []
    
    for table in table_names:
        try:
            print(f"\n=== Benchmarking {table} ===")
            
            # Warm-up run
            print("Running warm-up...")
            benchmark_query(table, limit=1)
            
            # Actual benchmark
            print("Running benchmark...")
            result = benchmark_query(table, limit=limit)
            results.append(result)
            
            # Print results
            print(f"Results for {table}:")
            print(f"Execution time: {result['execution_time']:.4f} seconds")
            print(f"Rows returned: {result['rows_returned']}")
            print(f"Rows per second: {result['rows_per_second']:.2f}")
            
        except Exception as e:
            print(f"Error benchmarking table {table}: {str(e)}")
    
    return results


if __name__ == "__main__":
    
    try:
        # # Show database information
        # print("\n**** Database Information ****")
        # get_table_info()
        
        # # Show schema for asset_master
        # print("\n**** Table Schema ****")
        # get_table_schema("asset_master")
        
        # # Run benchmark
        # print("\n**** Running Benchmarks ****")
        # run_benchmark(limit=10_000_000)
        
        # Run example queries
        print("\n**** Example Queries ****")
        example_queries()


    except Exception as e:
        print(f"\nError: {e}")
    

