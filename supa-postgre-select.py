#postgreSQL 

from sqlalchemy import create_engine, text

CONNECTION_STRING = "postgresql://postgres.ju~~~~md:F26~passwd~~o@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

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

if __name__ == "__main__":
    print("=-"*10,"start!")
    use_case_01()
    print("=-"*10)
    use_case_02()
    print("=-"*10,"done!")


