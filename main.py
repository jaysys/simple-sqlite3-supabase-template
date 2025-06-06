import os
import pprint
from sqlalchemy import create_engine, text, MetaData
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
# DATABASE_URL=postgresql://postgres.roe~~~~ofpsl:pass~~word@aws-0-ap-no~~.pooler.s~~~base.com:6543/postgres
CONNECTION_STRING = os.getenv('DATABASE_URL')
if not CONNECTION_STRING:
    raise ValueError("DATABASE_URL not found in environment variables")

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

    one = result_set.fetchone()
    #print(one)
    many = result_set.fetchmany(2)
    #print(many)
    all = result_set.fetchall() #이미 fetch된게 있으면 그 다음부터 전체, fetch된게 없으면 처음부터 전체 데이터 넘겨받음
    #print(all)
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

if __name__ == "__main__":
    print("=-"*10,"start!")
    # get_table_info()
    use_case_01()
    # use_case_02()
    # use_case_03()
    print("=-"*10,"done!")


