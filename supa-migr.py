import sqlite3
from sqlalchemy import create_engine, text

# SQLite3 DB 연결 [SOURCE]
sqlite_db_file = './db/m3_myasset.sqlite3'
conn_sqlite = sqlite3.connect(sqlite_db_file)
cursor_sqlite = conn_sqlite.cursor()
'''
sqlite> select * from my_asset limit 10;
index  div     asset  qty               unit_usd              unit_krw     total_krw         asset_note           timestamp                 
-----  ------  -----  ----------------  --------------------  -----------  ----------------  -------------------  --------------------------
0      CRYPTO  MATIC  10002.6892886571  0.816                 1131.38      11316842.6074008  Metamask             2022-09-17 18:15:48.821894
1      CRYPTO  SAND   0.0               0.88                  1220.11      0.0               Metamask             2022-09-17 18:15:48.821894
2      CRYPTO  SAND   7263.3546710758   0.88                  1220.11      8862091.6677263   Sandbox Staked       2022-09-17 18:15:48.821894
ß'''

# SQLite3에서 이관할 데이터 조회 [SOURCE]
select_query = "SELECT * FROM my_asset"
cursor_sqlite.execute(select_query)


# PostgreSQL DB 연결 [TARGET]
postgres_connection_string = "postgresql://postgres.blablablabla:dbpasswd@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"
engine_postgres = create_engine(postgres_connection_string)
'''
create table
  public.my_asset (
    index smallint null,
    div text null,
    asset text null,
    qty real null,
    unit_usd real null,
    unit_krw real null,
    total_krw real null,
    asset_note text null,
    timestamp timestamp with time zone null,
    seq uuid not null default gen_random_uuid (),
    constraint my_asset_pkey primary key (seq),
    constraint my_asset_seq_key unique (seq)
  ) tablespace pg_default;
'''


# PosgreSQL DB insert query [TARGET]
insert_query = text("""
    INSERT INTO my_asset (index, div, asset, qty, unit_usd, unit_krw, total_krw, asset_note, timestamp) 
    VALUES (:index, :div, :asset, :qty, :unit_usd, :unit_krw, :total_krw, :asset_note, :timestamp)
""")

# 이관 배치 단위 
batch_size = 1000

# Fetch data from SQLite and insert into PostgreSQL
while True:
    batch = cursor_sqlite.fetchmany(batch_size)
    if not batch:
        break
    
    # Prepare data for insertion
    rows = [row for row in batch]
   
    # Execute insert query with parameterized values
    with engine_postgres.connect() as conn_postgres:
        print('.', end="")
        for row in rows:
            # Execute the insert query
            conn_postgres.execute(insert_query, {
                "index": row[0],
                "div": row[1],
                "asset": row[2],
                "qty": row[3],
                "unit_usd": row[4],
                "unit_krw": row[5],
                "total_krw": row[6],
                "asset_note": row[7],
                "timestamp": row[8]
            })
            conn_postgres.commit()

# 연결 종료
conn_sqlite.close()
