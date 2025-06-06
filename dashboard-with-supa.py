# PostgreSQ
import pandas as pd
import streamlit as st
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Asset Tracking Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-box {
        background-color: #2d2d2d;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #4CAF50;
    }
    .metric-label {
        font-size: 14px;
        color: #9e9e9e;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_engine():
    conn_str = os.getenv('DATABASE_URL')
    if not conn_str:
        st.error("DATABASE_URL not found in environment variables")
        st.stop()
    return create_engine(conn_str)

# Fetch data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_asset_history(days):
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    with get_engine().connect() as conn:
        # Fetch all data points for the selected date range
        query = f"""
            SELECT timestamp, total
            FROM asset_total_history_report 
            WHERE timestamp >= '{start_date}'
            ORDER BY timestamp
        """
        df = pd.read_sql_query(query, conn)
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
    return df

def resample_data(df, days):
    """Resample data based on the selected time range with proportional scaling
    
    Args:
        df: DataFrame with timestamp index and total values
        days: Number of days in the selected date range
        
    Returns:
        tuple: (resampled_data, timeframe_string)
    """
    # Calculate the timeframe in minutes (proportional to days, min 30min, max 1440min/24h)
    max_days = 90  # Maximum days for scaling
    min_minutes = 30  # Minimum timeframe in minutes
    max_minutes = 24 * 60  # Maximum timeframe in minutes (24 hours)
    
    # Calculate proportional minutes (linear scaling between min and max)
    if days <= 1:
        minutes = min_minutes  # Minimum 30 minutes for very short ranges
    else:
        # Scale proportionally between min and max minutes based on days
        ratio = min(days / max_days, 1.0)  # Cap at 1.0 for ranges > max_days
        minutes = min_minutes + (max_minutes - min_minutes) * ratio
    
    # Convert to nearest standard timeframe
    if minutes < 60:  # Less than 1 hour
        timeframe = f"{int(30 * round(minutes/30))}T"  # Round to nearest 30 minutes
        display_name = f"{int(30 * round(minutes/30))}분봉"
    elif minutes < 1440:  # Less than 1 day
        hours = max(1, round(minutes / 60))
        timeframe = f"{hours}h"  # Changed from 'H' to 'h' to fix deprecation warning
        display_name = f"{hours}시간봉"
    else:  # 1 day or more
        timeframe = "1D"
        display_name = "일봉"
    
    # Resample the data
    resampled = df['total'].resample(timeframe).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).dropna()
    
    return resampled, display_name

def main():
    st.title('📈 Asset Value Dashboard')
    
    # Sidebar controls
    st.sidebar.header('Filters')
    days = st.sidebar.slider('Time Range (days)', 7, 365, 90)
    
    # Fetch data
    df = fetch_asset_history(days)
    
    if df.empty:
        st.warning("No data available for the selected time range.")
        return
    
    # Calculate metrics
    latest_value = df['total'].iloc[-1]
    first_value = df['total'].iloc[0]
    value_change = latest_value - first_value
    pct_change = (value_change / first_value) * 100 if first_value != 0 else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
            <div class="metric-box">
                <div class="metric-label">Current Value</div>
                <div class="metric-value">₩{latest_value:,.0f}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
            <div class="metric-box">
                <div class="metric-label">Value Change ({days} days)</div>
                <div class="metric-value" style="color: {'#4CAF50' if value_change >= 0 else '#F44336'}">
                    {'+' if value_change >= 0 else ''}₩{abs(value_change):,.0f}
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
            <div class="metric-box">
                <div class="metric-label">Percentage Change</div>
                <div class="metric-value" style="color: {'#4CAF50' if pct_change >= 0 else '#F44336'}">
                    {'+' if pct_change >= 0 else ''}{pct_change:.2f}%
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Create candlestick chart
    st.markdown("### Asset Value (Candlestick Chart)")
    
    # Resample data based on the selected time range
    df_resampled, time_frame = resample_data(df, days)
    
    # Create candlestick figure with reversed colors
    fig = go.Figure(data=[go.Candlestick(
        x=df_resampled.index,
        open=df_resampled['open'],
        high=df_resampled['high'],
        low=df_resampled['low'],
        close=df_resampled['close'],
        increasing_line_color='#F44336',  # Red for increase
        increasing_fillcolor='#F44366',   # Lighter red fill
        decreasing_line_color='#4CAF50',  # Green for decrease
        decreasing_fillcolor='#66BB6A',   # Lighter green fill
        name=f'Candlestick ({time_frame})',
        line=dict(width=1)
    )])
    
    # Add timeframe indicator
    time_frame_map = {
        '1min': '1분봉',
        '1H': '1시간봉',
        '1D': '일봉'
    }
    st.sidebar.markdown(f"**Timeframe:** {time_frame_map.get(time_frame, time_frame)}")
    
    # # Add volume (optional)
    # df_resampled['volume'] = df_resampled['close'] - df_resampled['open']
    # fig.add_trace(go.Bar(
    #     x=df_resampled.index,
    #     y=df_resampled['volume'],
    #     name='Volume',
    #     marker_color=['#4CAF50' if x >= 0 else '#F44336' for x in df_resampled['volume']],
    #     opacity=0.3,
    #     showlegend=False,
    #     yaxis='y2'
    # ))
    
    # Add 7-day moving average
    df_resampled['MA7'] = df_resampled['close'].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x=df_resampled.index,
        y=df_resampled['MA7'],
        mode='lines',
        name='7-Day MA',
        line=dict(color='#FFA000', width=1.5)
    ))
    
    # Customize layout
    fig.update_layout(
        xaxis_title=None,
        yaxis_title='Total Value (₩)',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            showgrid=False,
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#2d2d2d',
            fixedrange=False,
            title='Price (₩)'
        ),
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    # Customize hover template for candlestick
    fig.update_traces(
        selector=dict(type='candlestick'),
        hovertext=df_resampled.apply(
            lambda x: f"Open: ₩{x['open']:,.0f}<br>High: ₩{x['high']:,.0f}<br>"
                      f"Low: ₩{x['low']:,.0f}<br>Close: ₩{x['close']:,.0f}",
            axis=1
        ),
        hoverinfo='text+x'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show raw data
    if st.checkbox('Show raw data'):
        st.subheader('Raw Data (Newest First)')
        st.dataframe(df.sort_index(ascending=False))

if __name__ == "__main__":
    main()
