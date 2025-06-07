import os
import time
import pprint
from sqlalchemy import create_engine, text, MetaData
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()
CONNECTION_STRING = os.getenv('DATABASE_URL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not all([CONNECTION_STRING, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Required environment variables not found. Please check DATABASE_URL, SUPABASE_URL, and SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_table_info():
    # Create an engine
    engine = create_engine(CONNECTION_STRING)
    conn = engine.connect()
    
    # 메타데이터 객체 생성 및 리플렉션
    meta = MetaData()
    meta.reflect(bind=engine, views=True)  # views=True로 뷰도 포함
    
    # 데이터베이스에서 뷰 목록 조회
    view_query = """
    SELECT table_name 
    FROM information_schema.views 
    WHERE table_schema = 'public';
    """
    
    # 테이블과 뷰 정보 출력
    def print_database_objects(meta, conn):
        # 테이블 목록 출력
        print("\n=== 테이블 목록 ===")
        for table_name in meta.tables.keys():
            print(f"테이블: {table_name}")
        
        # 뷰 목록 조회 및 출력
        print("\n=== 뷰 목록 ===")
        result = conn.execute(text(view_query))
        views = [row[0] for row in result]
        
        if not views:
            print("뷰가 존재하지 않습니다.")
        else:
            for view_name in views:
                print(f"뷰: {view_name}")
    
    # 테이블/뷰 스키마 출력
    def get_object_schema(object_name, meta=meta, conn=conn):
        # 테이블인지 확인
        if object_name in meta.tables:
            table = meta.tables[object_name]
            print(f"\n=== 테이블 '{object_name}' 스키마 ===")
            for column in table.columns:
                print(f"{column.name}: {column.type}")
        else:
            # 뷰인지 확인
            view_check = """
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' AND table_name = :view_name;
            """
            result = conn.execute(text(view_check), {'view_name': object_name}).fetchone()
            
            if result:
                # 뷰의 컬럼 정보 조회
                view_columns = """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = :view_name
                ORDER BY ordinal_position;
                """
                columns = conn.execute(text(view_columns), {'view_name': object_name})
                print(f"\n=== 뷰 '{object_name}' 스키마 ===")
                for col in columns:
                    print(f"{col[0]}: {col[1]}")
            else:
                print(f"\n'{object_name}' 테이블/뷰를 찾을 수 없습니다.")
    
    # 모든 객체 정보 출력
    print_database_objects(meta, conn)
    
    # 특정 테이블/뷰 스키마 확인 (예시로 'asset_master'와 'asset_total_history_report' 확인)
    get_object_schema("asset_master")
    get_object_schema("asset_total_history_report")

def conn_db_and_exec_query(stmt):
    engine = create_engine(CONNECTION_STRING)    
    with engine.connect() as conn:
        result_set = conn.execute(text(stmt))
        return result_set

def fetch_one_many_all_from_exec_query(stmt):  
    result_set = conn_db_and_exec_query(stmt)

    one = result_set.fetchone() #첫번째 1개 데이터
    many = result_set.fetchmany(2) #다음 2개의 데이터
    all = result_set.fetchall() #이미 fetch된게 있으면 그 다음부터 전체, fetch된게 없으면 처음부터 전체 데이터 넘겨받음
    return (one, many, all)


def fetch_all_from_exec_query(stmt):  
    result_set = conn_db_and_exec_query(stmt)

    all = result_set.fetchall() 
    return (all)


def use_case_01():
    query_stmt = """
        SELECT * 
        FROM asset_total_history_report 
        ORDER BY "timestamp"
        LIMIT 10;
    """  
    query_stmt_info = """
        SELECT count(*)
        FROM asset_total_history_report ;
    """  
    data = fetch_one_many_all_from_exec_query(query_stmt)
    data_info = fetch_one_many_all_from_exec_query(query_stmt_info)

    pprint.pprint(data)
    print("size", len(data[2]))
    pprint.pprint(data_info)


def use_case_02():
    query_stmt = """
        SELECT * 
        FROM asset_total_history_report 
        ORDER BY "timestamp"
        LIMIT 5;
    """  
    query_stmt_info = """
        SELECT count(*)
        FROM asset_total_history_report ;
    """  
    data = fetch_all_from_exec_query(query_stmt)
    data_info = fetch_all_from_exec_query(query_stmt_info)

    pprint.pprint(data)
    print("size", len(data))
    pprint.pprint(data_info)


def use_case_03():
    engine = create_engine(CONNECTION_STRING) 
    with engine.connect() as connection:
        # Build the select query
        select_query = """
        SELECT * 
        FROM asset_total_history_report 
        ORDER BY "timestamp" DESC 
        -- LIMIT 10
        """
        
        # Execute the query
        result_set = connection.execute(text(select_query))
        
        # Get column names from the result set
        columns = result_set.keys()
        
        # Print the results with column names
        for row in result_set:
            # Create a dictionary of column name to value
            row_dict = dict(zip(columns, row))
            # Print the last two columns dynamically
            last_two_columns = list(columns)[-2:]
            print(", ".join(f"{col}: {row_dict[col]}" for col in last_two_columns))


def benchmark_sqlalchemy_query(table_name: str, limit: int = 1000) -> dict:
    """Execute a simple SELECT query using SQLAlchemy and return timing information."""
    start_time = time.time()
    
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        # Simple select query
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        result = conn.execute(text(query))
        rows = result.fetchall()
        print(table_name, "rows", len(rows))
    
    end_time = time.time()
    
    return {
        'method': 'SQLAlchemy',
        'execution_time': end_time - start_time,
        'rows_returned': len(rows),
        'table': table_name,
        'limit': limit
    }

def benchmark_supabase_query(table_name: str, limit: int = 1000) -> dict:
    """Execute a simple SELECT query using Supabase client and return timing information."""
    start_time = time.time()
    
    # Using Supabase client to fetch data
    response = supabase.table(table_name).select('*').limit(limit).execute()
    rows = response.data if hasattr(response, 'data') else []
    print(table_name, "rows", len(rows))  

    end_time = time.time()
    
    return {
        'method': 'Supabase',
        'execution_time': end_time - start_time,
        'rows_returned': len(rows),
        'table': table_name,
        'limit': limit
    }

def run_benchmarks(limit: int = 900):
    """Run benchmarks for both SQLAlchemy and Supabase clients."""
    tables = ['asset_master', 'asset_total_history_report']
    results = []
    
    for table in tables:
        print("")
        try:
            # Warm-up run (not measured)
            benchmark_sqlalchemy_query(table, limit=1)
            benchmark_supabase_query(table, limit=1)
            
            # Actual benchmark runs
            sqlalchemy_result = benchmark_sqlalchemy_query(table, limit=limit)
            supabase_result = benchmark_supabase_query(table, limit=limit) # supabase client 를 이용하면 아무리 큰 limit 를 주더라도 1000개까지만 가져옴. 따라서 주의해야한다. 제대로 비교할려면 양 쪽 케이스 모두를 1000으로 설정해야한다.
            results.extend([sqlalchemy_result, supabase_result])
            
            # Calculate and print comparison
            faster = 'SQLAlchemy' if sqlalchemy_result['execution_time'] < supabase_result['execution_time'] else 'Supabase'
            time_diff = abs(sqlalchemy_result['execution_time'] - supabase_result['execution_time'])
            percentage = (time_diff / min(sqlalchemy_result['execution_time'], supabase_result['execution_time'])) * 100
            
            print(f"=== {table} Benchmark Results ===")
            print(f"SQLAlchemy: {sqlalchemy_result['execution_time']:.4f} seconds")
            print(f"Supabase:   {supabase_result['execution_time']:.4f} seconds")
            print(f"{faster} is {percentage:.2f}% faster")
            
        except Exception as e:
            print(f"Error benchmarking table {table}: {str(e)}")
    
    return results

if __name__ == "__main__":
    print("=-"*10,"start!")
    # Uncomment to see table info
    # get_table_info()
    
    # Example use cases 
    # use_case_01()
    # use_case_02()
    # use_case_03()

    # Run benchmarks
    run_benchmarks()

    print("\n","=-"*10,"done!")
