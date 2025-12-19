import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="FinSplit Dashboard", layout="wide")

st.title("📊 Transaction Analytics Dashboard")
st.markdown("Upload your report to see a daily breakdown of **Cash, UPI, and Portal** payments.")

# --- 1. File Upload ---
uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])

if uploaded_file:
    # Load data
    df = pd.read_excel(uploaded_file)
    
    # Sidebar Setup for Column Mapping
    st.sidebar.header("Map Your Columns")
    date_col = st.sidebar.selectbox("Date Column", df.columns)
    desc_col = st.sidebar.selectbox("Description/Mode Column", df.columns)
    amt_col = st.sidebar.selectbox("Amount Column", df.columns)

    # --- 2. Enhanced Logic ---
    def categorize_payment(description):
        desc = str(description).lower()
        if any(word in desc for word in ['upi', 'gpay', 'phonepe', 'vpa', 'paytm', 'bhim']):
            return 'UPI'
        elif any(word in desc for word in ['portal', 'razorpay', 'stripe', 'online', 'card', 'pos']):
            return 'Portal'
        elif any(word in desc for word in ['cash', 'hand', 'manual']):
            return 'Cash'
        else:
            return 'Other'

    # Process Data
    df[date_col] = pd.to_datetime(df[date_col]).dt.date
    df['Category'] = df[desc_col].apply(categorize_payment)
    
    # Create Daily Summary Table
    daily_summary = df.groupby([date_col, 'Category'])[amt_col].sum().unstack().fillna(0)

    # --- 3. Dashboard Metrics ---
    total_cash = df[df['Category'] == 'Cash'][amt_col].sum()
    total_upi = df[df['Category'] == 'UPI'][amt_col].sum()
    total_portal = df[df['Category'] == 'Portal'][amt_col].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cash", f"₹{total_cash:,.2f}")
    col2.metric("Total UPI", f"₹{total_upi:,.2f}")
    col3.metric("Total Portal", f"₹{total_portal:,.2f}")

    st.divider()

    # --- 4. Visualizations ---
    st.subheader("Daily Payment Trends")
    # Prepare data for plotting
    plot_df = daily_summary.reset_index().melt(id_vars=date_col, var_name='Category', value_name='Amount')
    
    fig = px.bar(plot_df, x=date_col, y='Amount', color='Category', 
                 barmode='group', title="Daily Split by Category")
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. Data View & Export ---
    st.subheader("Detailed Daily Breakdown")
    st.dataframe(daily_summary, use_container_width=True)

    csv = daily_summary.to_csv().encode('utf-8')
    st.download_button("📥 Download Daily Summary (CSV)", data=csv, file_name="daily_transaction_split.csv")
