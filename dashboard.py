# app.py
import streamlit as st
import pandas as pd
import plotly.express as px


#Data
@st.cache_data
def load_data(file):
    """
    Load data from an uploaded CSV file. The decorator @st.cache_data ensures
    that the data is loaded only once, improving performance.
    """
    df = pd.read_csv(file)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

# --- Fraud Detection Logic ---
def find_suspicious_emails(df):
    """
    Identify orders with suspicious email patterns, such as those from known
    disposable domains or using email aliasing with '+'.
    """
    disposable_domains = ['mailinator.com', 'temp-mail.org', '10minutemail.com', 'guerrillamail.com']
    suspicious_pattern = r'(@(' + '|'.join(disposable_domains) + r'))|\+'
    suspicious_df = df[df['customer_email'].str.contains(suspicious_pattern, regex=True, na=False)].copy()
    suspicious_df['fraud_reason'] = 'Disposable Domain or Email Alias'
    return suspicious_df

def main():
    #Page Configuration
    st.set_page_config(
        page_title="Analytics Dashboard",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    #Main
    st.title("🛒 Analytics Dashboard")

    #uploader
    uploaded_file = st.file_uploader("Choose a CSV file to inspect", type=["csv"])

    if uploaded_file is None:
        st.info("Please upload a CSV file with e-commerce data to begin analysis.", icon="☝️")
        st.stop()

    df = load_data(uploaded_file)

    #Sidebar
    st.sidebar.header("Dashboard Filters")

    # Date range selector
    min_date = df['order_date'].min().date()
    max_date = df['order_date'].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    #product categories
    all_categories = df['category'].unique()
    selected_categories = st.sidebar.multiselect("Select Product Category", all_categories, default=all_categories)

    #payment methods
    all_payments = df['payment_method'].unique()
    selected_payments = st.sidebar.multiselect("Select Payment Method", all_payments, default=all_payments)

    # Filtering
    filtered_df = df[
        (df['order_date'].dt.date >= start_date) &
        (df['order_date'].dt.date <= end_date) &
        (df['category'].isin(selected_categories)) &
        (df['payment_method'].isin(selected_payments))
    ]

    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your selections.", icon="⚠️")
        st.stop()

    #time-based analysis
    filtered_df['hour_of_day'] = filtered_df['order_date'].dt.hour
    filtered_df['day_of_week'] = filtered_df['order_date'].dt.day_name()


    # Metrics
    st.header("Overall Performance")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", f"{filtered_df.shape[0]:,}")
    with col2:
        st.metric("Total Revenue", f"${filtered_df['total_price'].sum():,.2f}")
    with col3:
        st.metric("Total Profit", f"${filtered_df['profit'].sum():,.2f}")
    with col4:
        st.metric("Pre-flagged Fraud", f"{filtered_df['is_fraud'].sum():,}")

    #Visualizations ---
    st.header("Detailed Analysis")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Performance Over Time",
        "🛍️ Product & Category Analysis",
        "📍 Geographic Insights",
        "🚨 Fraud Detection",
        "🌲 Sales Treemap"
    ])

    #Tab 1
    with tab1:
        st.subheader("Daily Performance and Time-Based Trends")

        #Daily Profit
        daily_profit = filtered_df.groupby(filtered_df['order_date'].dt.date)['profit'].sum().reset_index()
        fig_profit = px.line(daily_profit, x='order_date', y='profit', title="Daily Profit Over Time", labels={'order_date': 'Date', 'profit': 'Total Profit ($)'})
        st.plotly_chart(fig_profit, use_container_width=True)

        #Sales by Hour and Day of Week
        col_hour, col_day = st.columns(2)
        with col_hour:
            hourly_sales = filtered_df.groupby('hour_of_day')['total_price'].sum().reset_index()
            fig_hour = px.bar(hourly_sales, x='hour_of_day', y='total_price', title="Total Sales by Hour of Day")
            st.plotly_chart(fig_hour, use_container_width=True)
        with col_day:
            weekly_sales = filtered_df.groupby('day_of_week')['total_price'].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index()
            fig_week = px.bar(weekly_sales, x='day_of_week', y='total_price', title="Total Sales by Day of Week")
            st.plotly_chart(fig_week, use_container_width=True)

    #Tab 2
    with tab2:
        st.subheader("Most Popular Products & Categories")
        col_prod, col_cat = st.columns(2)
        with col_prod:
            product_counts = filtered_df['product_name'].value_counts().head(10).reset_index()
            fig_prod = px.bar(product_counts, x='count', y='product_name', orientation='h', title="Top 10 Most Popular Products")
            fig_prod.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_prod, use_container_width=True)
        with col_cat:
            category_counts = filtered_df['category'].value_counts().reset_index()
            fig_cat = px.pie(category_counts, values='count', names='category', title="Orders by Category", hole=0.3)
            st.plotly_chart(fig_cat, use_container_width=True)

    #Tab 3
    with tab3:
        st.subheader("Geographic Analysis of Sales and Fraud")
        map_metric = st.selectbox("Select Metric for Map Visualization", ["Total Sales", "Total Profit", "Fraudulent Orders"])

        if map_metric == "Total Sales":
            state_data = filtered_df.groupby('state')['total_price'].sum().reset_index()
            color_col, label = 'total_price', 'Total Sales'
        elif map_metric == "Total Profit":
            state_data = filtered_df.groupby('state')['profit'].sum().reset_index()
            color_col, label = 'profit', 'Total Profit'
        else:
            state_data = filtered_df[filtered_df['is_fraud'] == 1].groupby('state')['order_id'].count().reset_index().rename(columns={'order_id': 'fraud_count'})
            color_col, label = 'fraud_count', 'Number of Fraudulent Orders'

        fig_map = px.choropleth(state_data, locations='state', locationmode="USA-states", color=color_col, scope="usa", title=f"{label} by State")
        st.plotly_chart(fig_map, use_container_width=True)

    #Tab 4
    with tab4:
        st.subheader("Fraud Detection Analysis")

        # Anomaly Detection Scatter Plot
        st.write("#### Anomaly Detection: Price vs. Discount")
        fig_scatter = px.scatter(filtered_df, x='total_price', y='total_discount', color='is_fraud', hover_name='order_id', title="Order Price vs. Discount", color_discrete_map={0: 'blue', 1: 'red'})
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Email-Based Fraud
        st.write("#### Email-Based Fraud Pattern Detection")
        suspicious_email_orders = find_suspicious_emails(filtered_df)
        st.warning(f"Found {len(suspicious_email_orders)} orders with suspicious email patterns.", icon="📧")
        st.dataframe(suspicious_email_orders[['order_id', 'customer_name', 'customer_email', 'total_price', 'fraud_reason']])

    #Tab 5
    with tab5:
        st.subheader("Hierarchical Sales Distribution")
        fig_treemap = px.treemap(filtered_df, path=[px.Constant("All"), 'category', 'product_name'], values='total_price', title="Product Sales Treemap")
        st.plotly_chart(fig_treemap, use_container_width=True)

    #Data Inspector
    with st.expander("Show Filtered Data Inspector"):
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
