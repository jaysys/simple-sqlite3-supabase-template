from sqlalchemy import create_engine, text

# Define the connection string
connection_string = "postgresql://postgres.jutmv-aawmd:F26-passwd-qo@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

# Create an engine
engine = create_engine(connection_string)

# Function to execute SQL query
def get_query(stmt, engine=engine):
    with engine.connect() as conn:
        # Execute the query
        result = conn.execute(text(stmt))
        return result

# Sample query with limit and order by timestamp desc and index asc
def collect_data():
    query = """
        SELECT timestamp, index, div, asset, qty, unit_usd, unit_krw, total_krw 
        FROM my_asset 
        ORDER BY "timestamp" DESC, "index" ASC 
        LIMIT 10
    """    
    result = get_query(stmt = query)
    print(result.fetchone())
    print(result.fetchmany(2))
    results = result.fetchall()
    return results

# Example usage:
data = collect_data()
import pprint
pprint.pprint(data)
