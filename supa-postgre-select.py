#postgreSQL 

from sqlalchemy import create_engine, text

CONNECTION_STRING = "postgresql://postgres.ju~~~~md:F26~passwd~~o@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

if False:
    # Create an engine
    engine = create_engine(CONNECTION_STRING)
    conn = engine.connect()
    meta = MetaData()
    meta.reflect(bind=engine)

    # 테이블 목록 가져오기
    def get_table_names(meta=meta):
        table_names = meta.tables.keys()
        print("테이블 목록:")
        for table_name in table_names:
            print(table_name)

    # 테이블 스키마 가져오기
    def get_table_schema(table_name, meta=meta):
        table = meta.tables.get(table_name)
        if table is not None:
            print(f"테이블 '{table_name}'의 스키마:")
            for column in table.columns:
                print(f"{column.name}: {column.type}")
        else:
            print(f"테이블 '{table_name}'가 존재하지 않습니다.")
    get_table_names()  # 모든 테이블 목록 출력
    get_table_schema("my_asset")  # 특정 테이블의 스키마 출력

def conn_db_and_exec_query(stmt):
    engine = create_engine(CONNECTION_STRING)    
    with engine.connect() as conn:
        result_set = conn.execute(text(stmt))
        return result_set

def fetch_data_from_exec_query(stmt):  
    result_set = conn_db_and_exec_query(stmt)

    one = result_set.fetchone()
    #print(one)

    many = result_set.fetchmany(2)
    #print(many)
    
    all = result_set.fetchall() #이미 fetch된게 있으면 그 다음부터 전체, fetch된게 없으면 처음부터 전체 데이터 넘겨받음
    #print(all)
    
    return (one, many, all)

def use_case_01():
    query_stmt = """
        SELECT timestamp, index, div, asset, qty, unit_usd, unit_krw, total_krw 
        FROM my_asset 
        ORDER BY "timestamp" DESC, "index" ASC 
        LIMIT 10
    """  
    data = fetch_data_from_exec_query(query_stmt)
    
    import pprint
    pprint.pprint(data)

def use_case_02():
    engine = create_engine(CONNECTION_STRING) 
    with engine.connect() as connection:
        # Build the select query
        select_query = """
            SELECT * 
            FROM my_asset 
            ORDER BY timestamp DESC, index ASC 
            LIMIT 10
        """
        
        # Execute the query
        result_set = connection.execute(text(select_query))
        
        # Print the results
        for row in result_set:
            print(row)
            print(row[0], row[2])

if __name__ == "__main__":
    print("=-"*10,"start!")
    use_case_01()
    print("=-"*10)
    use_case_02()
    print("=-"*10,"done!")


