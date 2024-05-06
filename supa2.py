from sqlalchemy import create_engine, text

# Define the connection string
connection_string = "postgresql://postgres.jutblabla:dbpasswd@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

# Create an engine
engine = create_engine(connection_string)

# Sample query with limit and order by timestamp desc and index asc
with engine.connect() as connection:
    # Build the select query
    select_query = """
        SELECT * 
        FROM my_asset 
        ORDER BY "timestamp" DESC, "index" ASC 
        LIMIT 10
    """
    
    # Execute the query
    result = connection.execute(text(select_query))
    
    # Print the results
    for row in result:
        print(row)
