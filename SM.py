import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Global Stock Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR IMPROVED UX ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #1e293b; }
    div[data-testid="stMetricDelta"] { font-size: 1rem; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: STOCK SELECTION & HELPERS ---
st.sidebar.header("Stock Configuration")

# Popular suggestions to help the user get started
suggestions = {
    "Apple Inc. (AAPL)": "AAPL",
    "Microsoft Corp. (MSFT)": "MSFT",
    "NVIDIA Corp. (NVDA)": "NVDA",
    "Reliance Industries (RELIANCE.NS)": "RELIANCE.NS",
    "Sony Group Corp. (SONY)": "SONY"
}

selected_suggestion = st.sidebar.selectbox(
    "Suggested Stocks:",
    options=["Select a suggestion..."] + list(suggestions.keys())
)

# Determine the ticker to search
default_ticker = "AAPL"
if selected_suggestion != "Select a suggestion...":
    default_ticker = suggestions[selected_suggestion]

ticker_input = st.sidebar.text_input(
    "Or Enter Any Global Ticker Symbol:",
    value=default_ticker
).upper().strip()

# Time period selection
time_periods = {
    "1 Day": ("1d", "5m"),
    "1 Week": ("5d", "30m"),
    "1 Month": ("1mo", "1d"),
    "6 Months": ("6mo", "1d"),
    "1 Year": ("1y", "1d"),
    "5 Years": ("5y", "1d")
}

selected_period_label = st.sidebar.selectbox(
    "Select Chart Time Horizon:",
    options=list(time_periods.keys()),
    index=2 # Default to 1 Month
)

period, interval = time_periods[selected_period_label]

# --- MAIN PAGE CONTENT ---
st.title("📈 Global Stock Market Dashboard")
st.caption("Real-time data and historical trends powered by Yahoo Finance")

if ticker_input:
    try:
        # Fetch Data
        stock = yf.Ticker(ticker_input)
        
        # Get historical data for the chart
        df = stock.history(period=period, interval=interval)
        
        # Get live/current info
        info = stock.info
        long_name = info.get("longName", ticker_input)
        currency = info.get("currency", "USD")
        
        if df.empty:
            st.error(f"No data found for ticker '{ticker_input}'. Please check the symbol and try again.")
        else:
            # Header section
            st.subheader(f"{long_name} ({ticker_input})")
            
            # Calculate current price and delta changes
            current_price = df['Close'].iloc[-1]
            previous_close = df['Close'].iloc[0] if len(df) > 1 else current_price
            price_delta = current_price - previous_close
            price_delta_pct = (price_delta / previous_close) * 100

            # Metrics Layout
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label=f"Current Price ({currency})", 
                    value=f"{current_price:,.2f}", 
                    delta=f"{price_delta:+.2f} ({price_delta_pct:+.2f}%)"
                )
            with col2:
                high_price = df['High'].max()
                st.metric(label=f"{selected_period_label} High", value=f"{high_price:,.2f}")
            with col3:
                low_price = df['Low'].min()
                st.metric(label=f"{selected_period_label} Low", value=f"{low_price:,.2f}")

            st.markdown("---")

            # Chart Section
            st.write(f"### Historical Performance ({selected_period_label})")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=df['Close'], 
                mode='lines', 
                name='Close Price',
                line=dict(color='#2563eb', width=2.5)
            ))
            
            fig.update_layout(
                template="plotly_white",
                hovermode="x unified",
                xaxis_title="Date/Time",
                yaxis_title=f"Price ({currency})",
                margin=dict(l=20, r=20, t=20, b=20),
                height=450
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
else:
    st.info("Please enter or select a stock ticker from the sidebar to begin.")
