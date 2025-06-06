# PostgreSQL SUPABASE 이용한 대시보드

import time
import ccxt
import sqlite3
import pandas as pd
import datetime as dt
import pprint as pp
import altair as alt
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import app.common.util as util
import os
from sqlalchemy import create_engine, text, MetaData
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

st.set_page_config(
    page_title="J.Tracking",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "#This is an *extremely* cool app!"
    }
)


# Get database URL from environment variables
POSTGRES_CONN_STRING = os.getenv('DATABASE_URL')
if not POSTGRES_CONN_STRING:
    raise ValueError("DATABASE_URL not found in environment variables")

# Create engine
engine = create_engine(POSTGRES_CONN_STRING)

# Function to execute SQL query
def execute_query(stmt,engine=engine):
    conn = engine.connect()
    result = conn.execute(text(stmt))
    conn.close()
    return result.fetchall()


# 
def collect_crypto_data(hourly_interval=24, ticker=''):
    query = f"SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1;"
    results = execute_query(stmt=query)
    #print(">", results)

    dat_temp = [result[0] for result in results]
    latest_timestamp = dat_temp[0]
    #print(">>",latest_timestamp)

    # Calculate the timestamp for 24 hours ago from the current time
    ### 일단 막아놓고! end_time = latest_timestamp
    end_time = dt.datetime.now()
    start_time = end_time - dt.timedelta(hours = hourly_interval)

    # Format start_time and end_time as strings for the SQL query
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
    # print("Getting data between ", start_time_str, "and", end_time_str)

    # 데이터베이스에서 데이터 조회 (within the last 24 hours)
    if ticker == '':
        query = f"SELECT timestamp, SUM(total_krw) as tt FROM my_asset WHERE div = 'CRYPTO' and timestamp BETWEEN '{start_time}' AND '{end_time}' GROUP BY timestamp"
    else:
        query = f"SELECT timestamp, SUM(total_krw) as tt FROM my_asset where div = 'CRYPTO' and asset = '{ticker}' and timestamp BETWEEN '{start_time}' AND '{end_time}' GROUP BY timestamp, asset"

    results = execute_query(stmt=query)

    # 결과 데이터를 그래프용 리스트로 변환
    # timestamps = [dt.datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f") for result in results]
    timestamps = [result[0] for result in results]
    total_krw = [result[1] for result in results]
    latest_total_krw = results[-1][1]
    # print(latest_total_krw)

    data = {
        'timestamp': timestamps,
        'total_krw': total_krw
    }
    df = pd.DataFrame(data)

    latest = {
        'timestamp': latest_timestamp,
        'total_krw': latest_total_krw
    }
    
    return (df, latest)


'''
'''
def collect_stock_data(hourly_interval=24):
    query = f"SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1;"
    results = execute_query(stmt=query)

    dat_temp = [result[0] for result in results]
    latest_timestamp = dat_temp[0]
    #print(latest_timestamp)

    # Calculate the timestamp for 24 hours ago from the current time
    end_time = dt.datetime.now()
    start_time = end_time - dt.timedelta(hours = hourly_interval)

    # Format start_time and end_time as strings for the SQL query
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
    #print(start_time_str, end_time_str)

    # 데이터베이스에서 데이터 조회 (within the last 24 hours)
    query = f"SELECT timestamp, SUM(total_krw) as tt FROM my_asset WHERE div = 'STOCK' and timestamp BETWEEN '{start_time_str}' AND '{end_time_str}' GROUP BY timestamp"

    results = execute_query(stmt=query)

    # 결과 데이터를 그래프용 리스트로 변환
    # timestamps = [dt.datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f") for result in results]
    timestamps = [result[0] for result in results]
    total_krw = [result[1] for result in results]
    latest_total_krw = results[-1][1]
    # print(latest_total_krw)

    data = {
        'timestamp': timestamps,
        'total_krw': total_krw
    }
    df = pd.DataFrame(data)

    latest = {
        'timestamp': latest_timestamp,
        'total_krw': latest_total_krw
    }
    
    return (df, latest)

# a, b = collect_stock_data(hourly_interval=24)
# print("Latest stock 'total_krw' on SUPABASE is",b)

'''
'''
def collect_cash_data(hourly_interval=24):
    query = f"SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1;"
    results = execute_query(stmt=query)
    #print(results)

    dat_temp = [result[0] for result in results]
    latest_timestamp = dat_temp[0]
    #print(latest_timestamp)

    # Calculate the timestamp for 24 hours ago from the current time
    end_time = dt.datetime.now()
    start_time = end_time - dt.timedelta(hours = hourly_interval)

    # Format start_time and end_time as strings for the SQL query
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
    #print(start_time_str, end_time_str)

    # 데이터베이스에서 데이터 조회 (within the last 24 hours)
    query = f"SELECT timestamp, SUM(total_krw) as tt FROM my_asset WHERE div = 'CASH' and timestamp BETWEEN '{start_time_str}' AND '{end_time_str}' GROUP BY timestamp"
    results = execute_query(stmt=query)

    # 결과 데이터를 그래프용 리스트로 변환
    # timestamps = [dt.datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f") for result in results]
    timestamps = [result[0] for result in results]    
    total_krw = [result[1] for result in results]
    latest_total_krw = results[-1][1]
    # print(latest_total_krw)

    data = {
        'timestamp': timestamps,
        'total_krw': total_krw
    }
    df = pd.DataFrame(data)

    latest = {
        'timestamp': latest_timestamp,
        'total_krw': latest_total_krw
    }
    
    return (df, latest)

# a, b = collect_cash_data(hourly_interval=24)
# print("Latest cash 'total_krw' on SUPABASE is",b)

'''
'''
def collect_all_asset_data(hourly_interval=24):
    query = f"SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1;"
    results = execute_query(stmt=query)

    dat_temp = [result[0] for result in results]
    latest_timestamp = dat_temp[0]
    #print(latest_timestamp)

    # Calculate the timestamp for 24 hours ago from the current time
    end_time = dt.datetime.now()
    start_time = end_time - dt.timedelta(hours = hourly_interval)

    # Format start_time and end_time as strings for the SQL query
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
    #print(start_time_str, end_time_str)

    # 데이터베이스에서 데이터 조회 (within the last 24 hours)
    query = f"SELECT timestamp, SUM(total_krw) as tt FROM my_asset WHERE timestamp BETWEEN '{start_time_str}' AND '{end_time_str}' GROUP BY timestamp ORDER BY timestamp;"
    print(query)
    results = execute_query(stmt=query)


    # 결과 데이터를 그래프용 리스트로 변환
    # timestamps = [dt.datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f") for result in results]
    timestamps = [result[0] for result in results]   
    total_krw = [result[1] for result in results]
    latest_total_krw = results[-1][1]
    # print(latest_total_krw)

    data = {
        'timestamp': timestamps,
        'total_krw': total_krw
    }
    df = pd.DataFrame(data)

    latest = {
        'timestamp': latest_timestamp,
        'total_krw': latest_total_krw
    }

    return (df, latest)

# a, b = collect_all_asset_data(hourly_interval=24)
# print("Latest all 'total_krw' on SUPABASE is",b)


def qry_all():
    query = f"SELECT index,div,asset,qty,unit_usd,unit_krw,total_krw,asset_note,timestamp FROM my_asset WHERE timestamp = (SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1) order by total_krw desc;"
    rows = execute_query(stmt=query)
    df = pd.DataFrame(rows, columns=['index','div','asset','qty','usd','krw','total(krw)','note','date'])
    return(df)
# print(qry_all())

def qry_asset_sum():
    query = f"SELECT asset as Asset, sum(qty) as Quantity, sum(total_krw) as Total, timestamp as Date  FROM my_asset  WHERE (timestamp = (SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1) and total_krw > 0) group by timestamp, asset order by total desc;"
    rows = execute_query(stmt=query)
    df = pd.DataFrame(rows, columns=['Asset','Quantity','Total','Date'])
    return(df)
# print(qry_asset_sum())

def qry_div_sum():
    # conn = sqlite3.connect(DB_FILE)
    # with conn:
    #     cursor = conn.cursor()
    #     query = f"SELECT div, sum(total_krw) as Total, timestamp as Date  FROM my_asset  WHERE (timestamp = (SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1) and total_krw > 0) group by timestamp, div order by total desc;"
    #     cursor.execute(query)
    #     rows = cursor.fetchall()
    query = f"SELECT div, sum(total_krw) as Total, timestamp as Date  FROM my_asset  WHERE (timestamp = (SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1) and total_krw > 0) group by timestamp, div order by total desc;"
    rows = execute_query(stmt=query)
    df = pd.DataFrame(rows, columns=['div','Total','Date'])
    return(df)
# print(qry_div_sum())

def qry_cex_sum():
    query = f"SELECT asset_note as note, sum(total_krw) as Total, timestamp as Date  FROM my_asset  WHERE (timestamp = (SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1) and total_krw > 0) group by timestamp, note ORDER BY total desc;"
    rows = execute_query(stmt=query)
    df = pd.DataFrame(rows, columns=['note','Total','Date'])
    return(df)
# print(qry_cex_sum())

def qry_btc_prcice():
    query = f"SELECT avg(unit_krw), timestamp FROM my_asset WHERE (timestamp = (SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1) and asset = 'BTC') group by timestamp;"
    rows = execute_query(stmt=query)
    return (rows[0][0])
# print(qry_btc_prcice())

def qry_eth_prcice():
    query = f"SELECT avg(unit_krw), timestamp FROM my_asset WHERE (timestamp = (SELECT timestamp FROM my_asset ORDER BY timestamp DESC LIMIT 1) and asset = 'ETH') group by timestamp;"
    rows = execute_query(stmt=query)
    return (rows[0][0])   
# print(qry_eth_prcice())






'''
'''
def collecting_main_proc(title=None, hourly=24, ticker=''):

    match title:
        case "CRYPTO":
            df, latest = collect_crypto_data(hourly, ticker) 
        case "STOCK":
            df, latest = collect_stock_data(hourly)
        case "CASH":
            df, latest = collect_cash_data(hourly)
        case "ALL":
            df, latest = collect_all_asset_data(hourly)
        case _:
            print("[ERR] No data collected")
            df, latest = None, None
    return df, latest


'''
'''
def displaying_main_proc(title, ax, df, latest):
    # Plot using axes ('ax')
    color_ = 'red' if title == "CRYPTO" else 'green'
    ax.plot(df["timestamp"], df["total_krw"], marker='', linestyle='--', color=color_, linewidth=0.8, alpha=1, label=f'total_krw of {title}')

    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Total KRW')
    ax.yaxis.grid(True, linestyle=':', linewidth=0.8)

    ax.set_title(f'{title}: {"{:,.2f}".format(latest.get("total_krw"))} KRW, DB at {str(latest.get("timestamp"))}')
    ax.legend()

    # Adjust x-axis labels for ax1
    num_labels = min(10, len(df["timestamp"]))  # Limit the number of x-axis labels to 10 or the number of timestamps if less
    step = len(df["timestamp"]) // num_labels  # Calculate step size for label selection
    selected_labels = [df["timestamp"][i] for i in range(0, len(df["timestamp"]), step)]  # Select labels with the calculated step
    selected_labels_str = [dt.strftime("%Y-%m-%d") for dt in selected_labels]  # Convert selected labels to strings
    ax.set_xticks(selected_labels)  # Set the x-axis tick positions
    ax.set_xticklabels(selected_labels_str, rotation=30)  # Set the x-axis tick labels


'''
'''
def main():
    krw = util.usd2krw(1)

    tab_001, tab_002, tab_003, tab_004 = st.tabs(["SB (1)총액추이", "(2)크립토별추이", "(3)상세테이블", "(4)장기추이" ])

    df = qry_div_sum() #'div','Total','Date'
    total_krw_sum = df['Total'].sum()
    total_btc_sum = total_krw_sum/qry_btc_prcice()
    total_eth_sum = total_krw_sum/qry_eth_prcice()
    df["Ratio"] = df['Total'] / total_krw_sum * 100 
    df["Total"] = df["Total"].apply(lambda x: "{:,.0f}".format(x))  # Format the column with commas
    df["Ratio"] = df["Ratio"].apply(lambda x: "{:,.2f}".format(x))

    with tab_001:
        st.markdown(f"# 총액 \u20A9{total_krw_sum:,.0f}(원)  |  {total_btc_sum:,.3f}(BTC)  |  {total_eth_sum:,.3f}(ETH)")
        st.markdown("#### 전체 금액 추이")      
        import pytz

        # data_timezone = pytz.UTC
        data_timezone = pytz.timezone('Asia/Seoul')
        
        daily = st.slider('몇 일간의 총액자산추이를 보고싶나요?', 1, 30, 1)
        # st.write("아래 그래프는 최근 " + str(daily) + '일간 자산 총금액 변동 추이입니다')        
        df, latest = collecting_main_proc("ALL", int(daily * 24))

        data = df
        data['timestamp'] = data['timestamp'].dt.tz_convert(data_timezone)  # Set the timezone to Asia/Seoul
        # print(data)

        chart = alt.Chart(data).mark_line(color='red', strokeWidth=1, strokeDash=[3,1] ).encode(
            x=alt.X('timestamp', axis=alt.Axis(title='Datetime', format='%m/%d(%H시)', grid=True, labelAngle=0, labelAlign='center')),
            y=alt.Y('total_krw:Q', axis=alt.Axis(title='Total KRW (원)', format='~s'), scale=alt.Scale(zero=False))
        ).properties(
            title='All asset',
            width=600,  # Set the width of the chart
            height=350  # Set the height of the chart
        )
        st.altair_chart(chart, theme="streamlit", use_container_width=True)

        # st.markdown("- 크립토 요약")
        df = qry_all()
        # 'div' 열이 "CRYPTO"인 행만 필터링
        crypto_df = df[df['div'] == 'CRYPTO']
        # 'asset'을 기준으로 그룹화하고 'qty' 및 'total(krw)' 열을 합산
        result = crypto_df.groupby('asset').agg({
            'div': 'first',
            'qty': 'sum',
            'total(krw)': 'sum',  # total(krw)의 합계 추가
            'date': 'first',
        }).reset_index()
        
        # 'ratio' 열 추가 %rate
        crypto_total_krw_sum = result['total(krw)'].sum()
        result['ratio'] = result['total(krw)'] / crypto_total_krw_sum * 100

        # 'total(krw)' 열을 내림차순으로 정렬
        # asset div qty total(krw) ratio date
        df = result.sort_values(by='total(krw)', ascending=False)

        # print("cryto total:", result['total(krw)'].sum())
        # print(result)

        df["total(krw)"] = df["total(krw)"].apply(lambda x: "{:,.0f}".format(x)) 
        df["qty"] = df["qty"].apply(lambda x: "{:,.3f}".format(x))  # Format the column with commas
        df['ratio'] = df['ratio'].apply(lambda x: f'{x:,.2f}')

        st.write(f"#### 크립토 {crypto_total_krw_sum:,.0f}(원) 구성비율")
        st.dataframe(data = df, 
                     hide_index=True, 
                     column_order=("asset","div","qty","total(krw)","ratio","date" ),
                     use_container_width=True,
                     column_config= {"total(krw)": st.column_config.NumberColumn("보유금액(원)",help="Total KRW 입니다",),
                                    "qty":st.column_config.NumberColumn("보유수량"), 
                                    "ratio":st.column_config.NumberColumn("구성비율(%)"), 
                                    "date": st.column_config.DatetimeColumn("조회일자",format="YYYY MMM D, h:mm a"),
                                    }
                    )




    with tab_002:
        st.markdown(f"# 총액 \u20A9{total_krw_sum:,.0f}(원)  |  {total_btc_sum:,.3f}(BTC)  |  {total_eth_sum:,.3f}(ETH)")
        st.markdown("#### 개별 추이")      
        import pytz

        # data_timezone = pytz.UTC
        data_timezone = pytz.timezone('Asia/Seoul')
        daily2 = st.slider('원하는 간격을 선택하세요', 1, 30, 7)

        df, latest = collecting_main_proc("CRYPTO", int(daily2 * 24), ticker='SOL')
        data = df
        data['timestamp'] = data['timestamp'].dt.tz_convert(data_timezone)  # Set the timezone to Asia/Seoul
        # print(data)
        chart = alt.Chart(data).mark_line(color='red', strokeWidth=1, strokeDash=[3,1] ).encode(
            x=alt.X('timestamp', axis=alt.Axis(title='Datetime', format='%m/%d(%H시)', grid=True, labelAngle=0, labelAlign='center')),
            y=alt.Y('total_krw:Q', axis=alt.Axis(title='Total KRW (원)', format='~s'), scale=alt.Scale(zero=False))
        ).properties(
            title='Crypto SOL',
            width=600,  # Set the width of the chart
            height=350  # Set the height of the chart
        )
        st.altair_chart(chart, theme="streamlit", use_container_width=True)

        df, latest = collecting_main_proc("CRYPTO", int(daily2 * 24), ticker='BTC')
        data = df
        data['timestamp'] = data['timestamp'].dt.tz_convert(data_timezone)  # Set the timezone to Asia/Seoul
        # print(data)
        chart = alt.Chart(data).mark_line(color='red', strokeWidth=1, strokeDash=[3,1] ).encode(
            x=alt.X('timestamp', axis=alt.Axis(title='Datetime', format='%m/%d(%H시)', grid=True, labelAngle=0, labelAlign='center')),
            y=alt.Y('total_krw:Q', axis=alt.Axis(title='Total KRW (원)', format='~s'), scale=alt.Scale(zero=False))
        ).properties(
            title='Crypto BTC',
            width=600,  # Set the width of the chart
            height=350  # Set the height of the chart
        )
        st.altair_chart(chart, theme="streamlit", use_container_width=True)

        df, latest = collecting_main_proc("CRYPTO", int(daily2 * 24), ticker='FLR')
        data = df
        data['timestamp'] = data['timestamp'].dt.tz_convert(data_timezone)  # Set the timezone to Asia/Seoul
        # print(data)
        chart = alt.Chart(data).mark_line(color='red', strokeWidth=1, strokeDash=[3,1] ).encode(
            x=alt.X('timestamp', axis=alt.Axis(title='Datetime', format='%m/%d(%H시)', grid=True, labelAngle=0, labelAlign='center')),
            y=alt.Y('total_krw:Q', axis=alt.Axis(title='Total KRW (원)', format='~s'), scale=alt.Scale(zero=False))
        ).properties(
            title='Crypto FLR',
            width=600,  # Set the width of the chart
            height=350  # Set the height of the chart
        )
        st.altair_chart(chart, theme="streamlit", use_container_width=True)

        df, latest = collecting_main_proc("CRYPTO", int(daily2 * 24), ticker='ETH')
        data = df
        data['timestamp'] = data['timestamp'].dt.tz_convert(data_timezone)  # Set the timezone to Asia/Seoul
        # print(data)
        chart = alt.Chart(data).mark_line(color='red', strokeWidth=1, strokeDash=[3,1] ).encode(
            x=alt.X('timestamp', axis=alt.Axis(title='Datetime', format='%m/%d(%H시)', grid=True, labelAngle=0, labelAlign='center')),
            y=alt.Y('total_krw:Q', axis=alt.Axis(title='Total KRW (원)', format='~s'), scale=alt.Scale(zero=False))
        ).properties(
            title='Crypto ETH',
            width=600,  # Set the width of the chart
            height=350  # Set the height of the chart
        )
        st.altair_chart(chart, theme="streamlit", use_container_width=True)        





    with tab_003:
        st.markdown(f"# 총액 \u20A9{total_krw_sum:,.0f}(원)  |  {total_btc_sum:,.3f}(BTC)  |  {total_eth_sum:,.3f}(ETH)")        
        df = qry_div_sum() #'div','Total','Date'
        total_krw_sum = df['Total'].sum()
        total_btc_sum = total_krw_sum/qry_btc_prcice()
        total_eth_sum = total_krw_sum/qry_eth_prcice()
        df["Ratio"] = df['Total'] / total_krw_sum * 100 
        df["Total"] = df["Total"].apply(lambda x: "{:,.0f}".format(x))  # Format the column with commas
        df["Ratio"] = df["Ratio"].apply(lambda x: "{:,.2f}".format(x))
        
        st.dataframe(data = df, 
                     hide_index=True, 
                     column_order=("div","Total","Ratio","Date"),
                     use_container_width=True,
                     column_config= {"Total": st.column_config.NumberColumn("보유금액(원)",help="Total KRW 입니다",),
                                     "Ratio": st.column_config.NumberColumn("보유비율(%)"),
                                    "Date": st.column_config.DatetimeColumn("조회일자",format="YYYY MMM D, h:mm a"),
                                    }
                    )

        st.markdown(f"#### 거래소별 보유금액")
        df = qry_cex_sum() #'note','Total','Date'
        total_krw_sum = df['Total'].sum()
        total_btc_sum = total_krw_sum/qry_btc_prcice()
        total_eth_sum = total_krw_sum/qry_eth_prcice()
        df["Ratio"] = df['Total'] / total_krw_sum * 100 
        df["Total"] = df["Total"].apply(lambda x: "{:,.0f}".format(x))  # Format the column with commas
        df["Ratio"] = df["Ratio"].apply(lambda x: "{:,.2f}".format(x))
        st.dataframe(data = df, 
                     hide_index=True, 
                     column_order=("note","Total","Ratio","Date"),
                     use_container_width=True,
                     column_config= {"Total": st.column_config.NumberColumn("보유금액(원)",help="Total KRW 입니다",),
                                     "Ratio": st.column_config.NumberColumn("보유비율(%)"),
                                    "Date": st.column_config.DatetimeColumn("조회일자",format="YYYY MMM D, h:mm a"),
                                    }
                    )

        #target price
        first = 144_000_000
        second = 200_000_000   
        third = 440_000_000
        exiting = 1_000_000_000   
        f = lambda a, b: "Yet to go" if a - b < 0 else "<font color='red'>**Bravo!!!**</font>"

        st.markdown(f"- First target until **{first:,.0f}**: {((total_krw_sum - first)/first*100):,.2f}%, {f(total_krw_sum,first)}",  unsafe_allow_html=True)
        st.markdown(f"- Second target until **{second:,.0f}**: {((total_krw_sum - second)/second*100):,.2f}%, {f(total_krw_sum,second)}",unsafe_allow_html=True)
        st.markdown(f"- Third target until **{third:,.0f}**: {((total_krw_sum - third)/third*100):,.2f}%, {f(total_krw_sum,third)}", unsafe_allow_html=True)
        st.markdown(f"- Exit target until **{exiting:,.0f}**: {((total_krw_sum - exiting)/exiting*100):,.2f}%, {f(total_krw_sum,exiting)}",   unsafe_allow_html=True)

        st.markdown("#### 자산별 보유금액")
        df = qry_asset_sum() #'Asset','Quantity','Total','Date'
        df["Total"] = df["Total"].apply(lambda x: "{:,.0f}".format(x))  # Format the column with commas
        df["Quantity"] = df["Quantity"].apply(lambda x: "{:,.3f}".format(x))  # Format the column with commas
        st.dataframe(data = df, 
                     hide_index=True, 
                     column_order=("Asset","Quantity","Total","Date"),
                     use_container_width=True,
                     column_config= {"Total": st.column_config.NumberColumn("보유금액(원)"),
                        "Quantity":st.column_config.NumberColumn("자산수량"), 
                        "Date": st.column_config.DatetimeColumn("조회일자", format="YYYY MMM D, h:mm a"),
                        }
                    )


    with tab_004:
        st.markdown(f"# 총액 \u20A9{total_krw_sum:,.0f}(원)  |  {total_btc_sum:,.3f}(BTC)  |  {total_eth_sum:,.3f}(ETH)")

        st.markdown("#### 장기 추이")
        # if st.button("Refresh"):
        #     print("refreshing...", dt.datetime.now())
        #     st.rerun()    

        # str_qry_hr = st.text_input("Type query-hour-interval in, then press 'ENTER' ", 24)
        # hourly_interval = int(str_qry_hr)

        daily = st.slider('시간간격을 선택하세요', 1, 365*3, 90)
        hourly_interval = daily*24                
        st.markdown(f"- 그래프는 {str(int(hourly_interval/24))}일간의 추이입니다. 조회시각은 {str(dt.datetime.now())} 입니다")

        # fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10,17)) 
        fig, (ax1) = plt.subplots(1, 1, figsize=(14,7)) 

        df, latest = collecting_main_proc("ALL", hourly_interval)
        print(df, latest)
        displaying_main_proc("ALL", ax1, df, latest)

        # df, latest = collecting_main_proc("STOCK", hourly_interval)
        # displaying_main_proc("STOCK", ax3, df, latest)
        # df, latest = collecting_main_proc("CASH", hourly_interval)
        # displaying_main_proc("CASH", ax4, df, latest)

        # df, latest = collecting_main_proc("CRYPTO", hourly_interval, ticker='BTC')
        # displaying_main_proc("BTC", ax2, df, latest)
        # df, latest = collecting_main_proc("CRYPTO", hourly_interval, ticker='SOL')
        # displaying_main_proc("SOL", ax1, df, latest)
        # df, latest = collecting_main_proc("CRYPTO", hourly_interval, ticker='ETH')
        # displaying_main_proc("ETH", ax4, df, latest)
        # df, latest = collecting_main_proc("CRYPTO", hourly_interval, ticker='FLR')
        # displaying_main_proc("FLR", ax3, df, latest)        

        fig.tight_layout()

        st.pyplot(fig)




'''
'''
if __name__ == "__main__":

    while True:
        main()
        time.sleep(300)
        print("re-running", dt.datetime.now())
        st.rerun()

    if False:
        print("/1/")
        a = qry_all()
        print(a)

        print("/2/")
        b = qry_asset_sum()
        print(b)

        print("/3/")
        c = qry_div_sum()
        print(c)

        print("/4/")    
        qry_cex_sum()

        print("/5/")
        e = collect_crypto_data(hourly_interval=24*100, ticker='FLR')
        print(e)



        


