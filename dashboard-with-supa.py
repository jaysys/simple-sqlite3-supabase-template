# PostgreSQ
import pandas as pd
import streamlit as st
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime, timedelta
import plotly.express as px

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
def fetch_asset_history(days=30):
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    with get_engine().connect() as conn:
        # Using direct parameter binding with f-string for the date
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

def main():
    st.title('📈 Asset Value Dashboard')
    
    # Sidebar controls
    st.sidebar.header('Filters')
    days = st.sidebar.slider('Time Range (days)', 7, 365, 30)
    
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
    
    # Create and display the chart
    st.markdown("### Asset Value Over Time")
    fig = px.line(
        df.reset_index(),
        x='timestamp',
        y='total',
        labels={'timestamp': 'Date', 'total': 'Total Value (₩)'},
        height=500
    )
    
    # Customize hover data
    fig.update_traces(
        hovertemplate="""
        <b>Date:</b> %{x|%Y-%m-%d %H:%M}<br>
        <b>Value:</b> ₩%{y:,.0f}<extra></extra>
        """
    )
    
    # Customize layout
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#2d2d2d')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show raw data
    if st.checkbox('Show raw data'):
        st.subheader('Raw Data (Newest First)')
        st.dataframe(df.sort_index(ascending=False))

if __name__ == "__main__":
    main()
