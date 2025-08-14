import streamlit as st
import pandas as pd
from io import BytesIO
import os
import plotly.express as px
from PIL import Image


# ✅ Excel file path
file_path = "sale_data.xlsx"

# Page configuration
st.set_page_config(
    page_title="Welburg Metal Pvt Ltd",
    page_icon="📊"
)

# Load data
@st.cache_data
def load_data(path):
    return pd.read_excel(path)

df = load_data(file_path)

# Sidebar navigation

page = st.sidebar.radio(
    "✨ Menu",
    (
        "🏠 Home",                    #1
        "📍 Dashboard",                 #2
        "💸 Sales",                  #3
        "🧑‍💼 Exec Txns",             #4
        "🧑‍💳 Cust Txns",            #5
        "🧾 Cust Dues",                    #6
        "🤝 Exec → Cust",             #7
        "📉 Exec Dues",              #8
        "📤 Exec Sales",            #9
        "🗓️ Date Summary",            #10
        "🏷️ Cust by Type",         #11
        "🗃️ Type Sales",           #12
        "📆 Daily Recap",           #13
        "📈 Performance",            #14
        "💸 Commissions",           #15
        "🛒 Products",                  #16
        "👨‍💻 Analyst Bio",           #17
        "💡 About"                   #18
    )
)

# 1. Main Dashboard (Start)
if page == "🏠 Home":
    st.header("🏢 WELBURG METAL PVT LTD.")
    st.title("🚀 Sales & Deposit Dashboard")

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Filter for current month
    today = pd.Timestamp.today()
    current_month = today.month
    current_year = today.year
    df_current_month = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]

    # Calculate current month metrics
    sales_amount = df_current_month["sales_amount"].sum()
    deposit_amount = df_current_month["paid_amount"].sum()
    sales_return = df_current_month["sales_return"].sum()
    customer_cashback = df_current_month["customer_cashback"].sum() if "customer_cashback" in df_current_month.columns else 0
    actual_sales = sales_amount - sales_return

    # Calculate total market due (all time)
    if "customer_outstanding" not in df.columns:
        df["customer_outstanding"] = (
            df["openning_balance"].fillna(0) +
            df["sales_amount"].fillna(0) -
            df["sales_return"].fillna(0) -
            df["paid_amount"].fillna(0) -
            df["customer_cashback"].fillna(0)
        )
    total_market_due = df["customer_outstanding"].sum()

    # Executive-wise sales and due (current month)
    exec_summary = df_current_month.groupby("sales_executive").agg({
        "sales_amount": "sum",
        "paid_amount": "sum"
    }).reset_index()
    exec_due = df.groupby("sales_executive")["customer_outstanding"].sum().reset_index().rename(columns={"customer_outstanding": "due_amount"})
    exec_summary = exec_summary.merge(exec_due, on="sales_executive", how="left").fillna(0)

    # Month-wise sales and deposit (bar chart)
    df['month'] = df['date'].dt.to_period('M').astype(str)
    month_summary = df.groupby('month').agg({
        "sales_amount": "sum",
        "paid_amount": "sum"
    }).reset_index()

    # --- Compact KPI Cards (4 columns + 1 below) ---
    def format_compact(val):
        if abs(val) >= 1_000_000:
            return f"{val/1_000_000:.2f}M"
        elif abs(val) >= 1_000:
            return f"{val/1_000:.2f}K"
        else:
            return f"{val:,.2f}"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Sales", format_compact(actual_sales))
    col2.metric("🏦 Deposit", format_compact(deposit_amount))
    col3.metric("🔄 Return", format_compact(sales_return))
    col4.metric("🧾 Due", format_compact(total_market_due))
    col5, col6 = st.columns(2)
    col5.metric("🎁 Cashback", format_compact(customer_cashback))
    col6.metric("📅 Month", today.strftime("%B %Y"))

    st.markdown("---")

    st.markdown("### Executive-wise Sales & Due (Current Month)")
    st.dataframe(exec_summary, use_container_width=True)
    st.markdown("---")

    # Bar chart: Month-wise sales and deposit
    st.markdown("### 📊 Month-wise Sales & Deposit")
    fig = px.bar(
        month_summary,
        x="month",
        y=["sales_amount", "paid_amount"],
        barmode="group",
        labels={"value": "Amount", "month": "Month", "variable": "Type"},
        title="Month-wise Sales & Deposit")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Bar chart: Executive-wise sales and due
    st.markdown("### 🧑‍💼 Executive-wise Sales Bar Chart (Current Month)" \
    "")
    fig_exec = px.bar(
        exec_summary,
        x="sales_executive",
        y=["sales_amount", "paid_amount", "due_amount"],
        barmode="group",
        labels={"value": "Amount", "sales_executive": "Executive", "variable": "Type"},
        title="Executive-wise Sales, Deposit & Due"
    )
    st.plotly_chart(fig_exec, use_container_width=True)
    st.markdown("---")
    # Line chart: Sales trend (last 6 months)
    st.markdown("### 📈 Sales Trend (Last 6 Months)")
    last_6_months = month_summary.tail(6)
    fig_trend = px.line(
        last_6_months,
        x="month",
        y="sales_amount",
        markers=True,
        title="Sales Trend (Last 6 Months)"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("---")
    # Top 10 Customers by Sales in Current Month
    st.markdown("### 🏅 Top 10 Customers by Sales (Current Month)")
    top_customers = df_current_month.groupby("customer_name")["sales_amount"].sum().reset_index().sort_values(by="sales_amount", ascending=False).head(10)
    st.dataframe(top_customers, use_container_width=True)
    st.markdown("---")


# 1. Main Dashboard (End)
    
# 2. Dashboard (Start)

elif page == "📍 Dashboard":
    st.header("🏢 WELBURG METAL PVT LTD")
    st.title("📊 Sales & Deposit Dashboard")

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Filter for current month
    today = pd.Timestamp.today()
    current_month = today.month
    current_year = today.year
    df_current_month = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]

    # Calculate current month metrics
    sales_amount = df_current_month["sales_amount"].sum()
    deposit_amount = df_current_month["paid_amount"].sum()
    sales_return = df_current_month["sales_return"].sum()
    customer_cashback = df_current_month["customer_cashback"].sum() if "customer_cashback" in df_current_month.columns else 0
    actual_sales = sales_amount - sales_return

    # Calculate total market due (all time)
    if "customer_outstanding" not in df.columns:
        df["customer_outstanding"] = (
            df["openning_balance"].fillna(0) +
            df["sales_amount"].fillna(0) -
            df["sales_return"].fillna(0) -
            df["paid_amount"].fillna(0) -
            df["customer_cashback"].fillna(0)
        )
    total_market_due = df["customer_outstanding"].sum()

    # Executive-wise sales and due (current month)
    exec_summary = df_current_month.groupby("sales_executive").agg({
        "sales_amount": "sum",
        "paid_amount": "sum"
    }).reset_index()
    exec_due = df.groupby("sales_executive")["customer_outstanding"].sum().reset_index().rename(columns={"customer_outstanding": "due_amount"})
    exec_summary = exec_summary.merge(exec_due, on="sales_executive", how="left").fillna(0)

    # Month-wise sales and deposit (bar chart)
    df['month'] = df['date'].dt.to_period('M').astype(str)
    month_summary = df.groupby('month').agg({
        "sales_amount": "sum",
        "paid_amount": "sum"
    }).reset_index()

    # KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("📅 Current Month", today.strftime("%B %Y"))
    col2.metric("💰 Sales Amount", f"{actual_sales:,.2f}")
    col3.metric("🏦 Deposit Amount", f"{deposit_amount:,.2f}")
    col4.metric("🔄 Sales Return", f"{sales_return:,.2f}")
    col5.metric("🎁 Cashback", f"{customer_cashback:,.2f}")
    col6.metric("🧾 Market Due", f"{total_market_due:,.2f}")

    st.markdown("---")

    # Executive-wise Sales & Due Table
    st.markdown("### Executive-wise Sales & Due (Current Month)")
    st.dataframe(exec_summary, use_container_width=True)

    st.markdown("---")

    # Executive-wise Sales Bar Chart
    st.markdown("### 🧑‍💼 Executive-wise Sales Bar Chart (Current Month)")
    fig_exec = px.bar(
        exec_summary,
        x="sales_executive",
        y=["sales_amount", "paid_amount", "due_amount"],
        barmode="group",
        labels={"value": "Amount", "sales_executive": "Executive", "variable": "Type"},
        title="Executive-wise Sales, Deposit & Due"
    )
    st.plotly_chart(fig_exec, use_container_width=True)

    st.markdown("---")

    # Month-wise sales and deposit bar chart
    st.markdown("### 📊 Month-wise Sales & Deposit")
    fig = px.bar(
        month_summary,
        x="month",
        y=["sales_amount", "paid_amount"],
        barmode="group",
        labels={"value": "Amount", "month": "Month", "variable": "Type"},
        title="Month-wise Sales & Deposit"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Sales Trend Line Chart (last 6 months)
    st.markdown("### 📈 Sales Trend (Last 6 Months)")
    last_6_months = month_summary.tail(6)
    fig_trend = px.line(
        last_6_months,
        x="month",
        y="sales_amount",
        markers=True,
        title="Sales Trend (Last 6 Months)"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("---")

    # Top 10 Customers by Sales in Current Month
    st.markdown("### 🏅 Top 10 Customers by Sales (Current Month)")
    top_customers = df_current_month.groupby("customer_name")["sales_amount"].sum().reset_index().sort_values(by="sales_amount", ascending=False).head(10)
    st.dataframe(top_customers, use_container_width=True)
# 2. Dashboard (End)




# 3. Sales History (Start)
elif page == "💸 Sales":
    st.write("# 📜 Sales History ")
    st.title("📊 Sales & Deposit Dashboard")

    # ✅ Customer Outstanding calculation
    df["customer_outstanding"] = (
        df["openning_balance"].fillna(0) +
        df["sales_amount"].fillna(0) -
        df["sales_return"].fillna(0)-
        df["paid_amount"].fillna(0) -
        df["customer_cashback"].fillna(0)
    )

    # ✅ Sales Executive Wise Summary
    st.subheader("Sales Executive Wise Summary")
    grouped_exec = df.groupby("sales_executive")[
        ["openning_balance", "sales_amount", "sales_return", "paid_amount", "customer_cashback","customer_outstanding"]
    ].sum().reset_index()

    # ✅ number columns format
    number_cols = [
        "openning_balance",
        "sales_amount",
        "sales_return", 
        "paid_amount", 
        "customer_cashback",
        "customer_outstanding"]
    st.dataframe(
        grouped_exec.style.format({col: "{:,.2f}" for col in number_cols}),
        use_container_width=True
    )
    st.success("Total Outstanding Amount: {:.2f} BDT".format(df["customer_outstanding"].sum()))
    st.success("Total Sales Amount: {:.2f} BDT".format(df["sales_amount"].sum()))
    st.success("Total Deposit Amount: {:.2f} BDT".format(df["paid_amount"].sum()))
    st.success("Total Sales Return: {:.2f} BDT".format(df["sales_return"].sum()))
    st.success("Total Customer Cashback: {:.2f} BDT".format(df["customer_cashback"].sum()))
    st.success("Total Executive Commission: {:.2f} BDT".format(df["executive_commission"].sum()))
    st.success("Total Team Leader Commission: {:.2f} BDT".format(df["teamleader_commission"].sum()))
    st.success("Total GM Commission: {:.2f} BDT".format(df["gm_commission"].sum()))
    
    st.markdown("---")


    # ✅ Sales Executive Selection
    executives = df["sales_executive"].dropna().unique()
    selected_exec = st.selectbox("🔍 Select Sales Executive", executives)

    # ✅ Filter Data for Selected Executive
    filtered_df = df[df["sales_executive"] == selected_exec]
    st.subheader(f"📄 Detailed Transactions for: {selected_exec}")
    st.dataframe(filtered_df)
    st.success(f"Total Outstanding for {selected_exec}: {filtered_df['customer_outstanding'].sum():,.2f} BDT")
    st.success(f"Total Sales Amount for {selected_exec}: {filtered_df['sales_amount'].sum():,.2f} BDT")
    st.success(f"Total Deposit Amount for {selected_exec}: {filtered_df['paid_amount'].sum():,.2f} BDT")
    st.success(f"Total Sales Return for {selected_exec}: {filtered_df['sales_return'].sum():,.2f} BDT")
    st.success(f"Total Customer Cashback for {selected_exec}: {filtered_df['customer_cashback'].sum():,.2f} BDT")
    st.markdown("---")
    # ✅ Download Button for Executive Transactions
    output_exec = BytesIO()
    filtered_df.to_excel(output_exec, index=False, engine='openpyxl')
    output_exec.seek(0)
    st.download_button(
        label="Download Executive Transactions as Excel",
        data=output_exec,
        file_name=f"{selected_exec}_transactions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="exec_download"
    )
    st.markdown("---")
    

# 3. Sales History (End)


# 4. Executive-wise Transactions (Start)
elif page == "🧑‍💼 Exec Txns":
    # --- Executive-wise Section ---
    st.header("Executive-wise Transactions")
    executives = df["sales_executive"].dropna().unique()
    selected_exec = st.selectbox("Select Sales Executive", executives, key="exec")

    # Calculate customer_outstanding if not already present
    if "customer_outstanding" not in df.columns:
        df["customer_outstanding"] = (
            df["openning_balance"].fillna(0) +
            df["sales_amount"].fillna(0) -
            df["sales_return"].fillna(0)-
            df["paid_amount"].fillna(0) -
            df["customer_cashback"].fillna(0)
        )

    # Date range for executive
    min_date, max_date = df["date"].min(), df["date"].max()
    exec_date_range = st.date_input("Select Date Range (Executive)", [min_date, max_date], key="exec_date")

    exec_filtered = df[
       (df["sales_executive"] == selected_exec) &
       (df["date"] >= pd.to_datetime(exec_date_range[0])) &
       (df["date"] <= pd.to_datetime(exec_date_range[1]))
    ]

    st.subheader(f"All Transactions for: {selected_exec}")
    st.dataframe(exec_filtered, use_container_width=True)
    st.success(f"Total Outstanding: {exec_filtered['customer_outstanding'].sum():,.2f} BDT")
    st.success(f"Sales Amount: {exec_filtered['sales_amount'].sum():,.2f} BDT")
    st.success(f"Deposit Amount: {exec_filtered['paid_amount'].sum():,.2f} BDT")
    st.success(f"Sales Return: {exec_filtered['sales_return'].sum():,.2f} BDT")
    st.success(f"Customer Cashback: {exec_filtered['customer_cashback'].sum():,.2f} BDT")
    st.success(f"Executive Commission: {exec_filtered['executive_commission'].sum():,.2f} BDT")


    # Download button for executive
    output_exec = BytesIO()
    exec_filtered.to_excel(output_exec, index=False, engine='openpyxl')
    output_exec.seek(0)
    st.download_button(
        label="Download Executive Transactions as Excel",
        data=output_exec,
        file_name=f"{selected_exec}_transactions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="exec_download"
    )

# 4. Executive-wise Transactions (End)


# 5. Customer-wise Transactions (Start)
elif page == "🧑‍💳 Cust Txns":
    # --- Customer-wise Section ---
    st.header("Customer-wise Transactions")
    customers = df["customer_name"].dropna().unique()
    selected_customer = st.selectbox("Select Customer", customers, key="cust")

    # Calculate customer_outstanding if not already present
    if "customer_outstanding" not in df.columns:
        df["customer_outstanding"] = (
            df["openning_balance"].fillna(0) +
            df["sales_amount"].fillna(0) -
            df["sales_return"].fillna(0)-
            df["paid_amount"].fillna(0)-
            df["customer_cashback"].fillna(0)
        )

    # Date range for customer
    min_date, max_date = df["date"].min(), df["date"].max()
    cust_date_range = st.date_input("Select Date Range (Customer)", [min_date, max_date], key="cust_date")

    cust_filtered = df[
        (df["customer_name"] == selected_customer) &
        (df["date"] >= pd.to_datetime(cust_date_range[0])) &
        (df["date"] <= pd.to_datetime(cust_date_range[1]))
    ]

    st.subheader(f"All Transactions for: {selected_customer}")
    st.dataframe(cust_filtered, use_container_width=True)
    st.success(f"Total Outstanding: {cust_filtered['customer_outstanding'].sum():,.2f} BDT")
    st.success(f"Sales Amount: {cust_filtered['sales_amount'].sum():,.2f} BDT")   
    st.success(f"Paid Amount: {cust_filtered['paid_amount'].sum():,.2f} BDT")  
    st.success(f"Sales Return: {cust_filtered['sales_return'].sum():,.2f} BDT")
    st.success(f"Cashback: {cust_filtered['customer_cashback'].sum():,.2f} BDT")


    # Download button for customer
    output_cust = BytesIO()
    cust_filtered.to_excel(output_cust, index=False, engine='openpyxl')
    output_cust.seek(0)
    st.download_button(
        label="Download Customer Transactions as Excel",
        data=output_cust,
        file_name=f"{selected_customer}_transactions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="cust_download"
    )
# 5. Customer-wise Transactions (End)

# 6. Customer Outstanding (Start)
elif page == "🧾 Cust Dues":
    st.header("📅 Customer-wise Date Range Summary")

    # 1. Select customer
    customer_list = sorted(df["customer_name"].dropna().unique())
    selected_customer = st.selectbox("Select Customer for Summary", customer_list, key="summary_customer")

    # 2. Select date range
    min_date, max_date = df['date'].min(), df['date'].max()
    cust_range = st.date_input(
        "Select Date Range for Customer Summary",
        [min_date, max_date],
        key="summary_customer_date"
    )

    # 3. Filter data
    cust_filtered = df[
        (df["customer_name"] == selected_customer) &
        (df["date"] >= pd.to_datetime(cust_range[0])) &
        (df["date"] <= pd.to_datetime(cust_range[1]))
    ].copy()

    # 4. Calculate customer_outstanding if not already present
    if "customer_outstanding" not in cust_filtered.columns:
        cust_filtered["customer_outstanding"] = (
            cust_filtered["openning_balance"].fillna(0) +
            cust_filtered["sales_amount"].fillna(0) -
            cust_filtered["sales_return"].fillna(0)-
            cust_filtered["paid_amount"].fillna(0) -
            cust_filtered["customer_cashback"].fillna(0)
        )

    # 5. Calculate totals
    cust_totals = {
        "Total Sales": cust_filtered["sales_amount"].sum(),
        "Total Deposit": cust_filtered["paid_amount"].sum(),
        "Total Return": cust_filtered["sales_return"].sum(),
        "Total Customer Cashback": cust_filtered["customer_cashback"].sum() if "customer_cashback" in cust_filtered.columns else 0,
        "Total Outstanding": cust_filtered["customer_outstanding"].sum()
    }

    # 6. Show totals
    st.subheader(f"Summary for {selected_customer} ({cust_range[0]} to {cust_range[1]})")
    for k, v in cust_totals.items():
        st.write(f"**{k}:** {v:,.2f}")

    # 7. Show transactions
    with st.expander("Show Transactions for Customer in Date Range"):
        st.dataframe(cust_filtered, use_container_width=True)

# 6. Customer Outstanding (End)

# 7. Executive wise customer (Start)

elif page == "🤝 Exec → Cust":
    st.header("Executive-wise Customer Transactions")
    
    # Select sales executive
    executives = df["sales_executive"].dropna().unique()
    selected_exec = st.selectbox("Select Sales Executive", executives, key="exec_cust")

    # Filter data for selected executive
    exec_filtered = df[df["sales_executive"] == selected_exec]

    # Select customer
    customers = exec_filtered["customer_name"].dropna().unique()
    selected_customer = st.selectbox("Select Customer", customers, key="exec_cust_select")

    # Filter data for selected customer
    cust_filtered = exec_filtered[exec_filtered["customer_name"] == selected_customer]

    # Show transactions
    st.subheader(f"Transactions for {selected_customer} by {selected_exec}")
    st.dataframe(cust_filtered, use_container_width=True)

    # Calculate customer_outstanding if not already present
    if "customer_outstanding" not in cust_filtered.columns:
        cust_filtered["customer_outstanding"] = (
            cust_filtered["openning_balance"].fillna(0) +
            cust_filtered["sales_amount"].fillna(0) -
            cust_filtered["sales_return"].fillna(0) -
            cust_filtered["paid_amount"].fillna(0) -
            cust_filtered["customer_cashback"].fillna(0)
        )
    # Show total outstanding for the customer
    total_outstanding = cust_filtered["customer_outstanding"].sum()
    st.success(f"Total Outstanding for {selected_customer}: {total_outstanding:,.2f} BDT")  
    # Show total sales and deposit for the customer
    total_sales = cust_filtered["sales_amount"].sum()
    total_deposit = cust_filtered["paid_amount"].sum()
    st.success(f"Total Sales for {selected_customer}: {total_sales:,.2f} BDT")
    st.success(f"Total Deposit for {selected_customer}: {total_deposit:,.2f} BDT")
    # Show total sales return and cashback for the customer
    total_return = cust_filtered["sales_return"].sum()
    total_cashback = cust_filtered["customer_cashback"].sum() if "customer_cashback" in cust_filtered.columns else 0
    st.success(f"Total Sales Return for {selected_customer}: {total_return:,.2f} BDT")
    st.success(f"Total Cashback for {selected_customer}: {total_cashback:,.2f} BDT")
    # Download button for executive customer transactions
    output_exec_cust = BytesIO()
    cust_filtered.to_excel(output_exec_cust, index=False, engine='openpyxl')
    output_exec_cust.seek(0)
    st.download_button(
        label="Download Executive Customer Transactions as Excel",
        data=output_exec_cust,
        file_name=f"{selected_exec}_{selected_customer}_transactions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="exec_cust_download"
    )



   

# 7. Executive wise customer (End)

# 8. Executive-wise Customer outstanding (Start)

elif page == "📉 Exec Dues":
    # Executive-wise, customer-wise total outstanding

    st.header("🔎 Executive-wise Customer Outstanding")

    # Select executive
    exec_names = sorted(df["sales_executive"].dropna().unique())
    selected_exec = st.selectbox("Select Sales Executive for Outstanding", exec_names, key="outstanding_exec")

    # Filter for selected executive
    exec_df = df[df["sales_executive"] == selected_exec].copy()

    # Calculate outstanding for each row if not already present
    # Use the correct columns from your Excel: openning_balance, sales_amount, sales_return, paid_amount, customer_cashback
    if "customer_outstanding" not in exec_df.columns:
        exec_df["customer_outstanding"] = (
            exec_df["openning_balance"].fillna(0)
            + exec_df["sales_amount"].fillna(0)
            - exec_df["sales_return"].fillna(0)
            - exec_df["paid_amount"].fillna(0)
            - exec_df["customer_cashback"].fillna(0)
        )

    # Group by customer and sum outstanding
    customer_outstanding = exec_df.groupby("customer_name")["customer_outstanding"].sum().reset_index()

    st.subheader(f"Customer-wise Total Outstanding for {selected_exec}")
    st.dataframe(customer_outstanding, use_container_width=True)

    # Show total outstanding amount for the executive
    total_outstanding = customer_outstanding["customer_outstanding"].sum()
    st.success(f"Total Outstanding Amount for {selected_exec}: {total_outstanding:,.2f} BDT")
    st.success(f"Total Sales Amount for {selected_exec}: {exec_df['sales_amount'].sum():,.2f} BDT")
    st.success(f"Total Deposit Amount for {selected_exec}: {exec_df['paid_amount'].sum():,.2f} BDT")
    st.success(f"Total Sales Return for {selected_exec}: {exec_df['sales_return'].sum():,.2f} BDT")
    st.success(f"Total Customer Cashback for {selected_exec}: {exec_df['customer_cashback'].sum():,.2f} BDT")
    # Download button for executive customer outstanding
    output_exec_outstanding = BytesIO()
    customer_outstanding.to_excel(output_exec_outstanding, index=False, engine='openpyxl')
    output_exec_outstanding.seek(0)

    st.download_button(
        label="Download Executive Customer Outstanding as Excel",
        data=output_exec_outstanding,
        file_name=f"{selected_exec}_customer_outstanding.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="exec_outstanding_download"
    )

# 8. Executive-wise Customer outstanding (End)

# 9. Executive Transaction (Start)
elif page == "📤 Exec Sales":
    st.header("📅 Executive-wise Sales, Deposit, Return & Customer Cashback (Custom Date Range)")

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Executive selection
    exec_names = sorted(df["sales_executive"].dropna().unique())
    selected_exec = st.selectbox("Select Sales Executive", exec_names, key="custom_exec")

    # Date range selection
    min_date, max_date = df['date'].min(), df['date'].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date], key="custom_exec_date")

    # Filter data
    filtered = df[
        (df["sales_executive"] == selected_exec) &
        (df["date"] >= pd.to_datetime(date_range[0])) &
        (df["date"] <= pd.to_datetime(date_range[1]))
    ].copy()

    # Show summary table
    summary = filtered.groupby("customer_name").agg({
        "sales_amount": "sum",
        "paid_amount": "sum",
        "sales_return": "sum",
        "customer_cashback": "sum",
        "executive_commission": "sum",
        "teamleader_commission": "sum",
        "gm_commission": "sum"
    }).reset_index()

    st.subheader(f"Summary for {selected_exec} ({date_range[0]} to {date_range[1]})")
    st.dataframe(summary, use_container_width=True)

    # Show totals
    totals = summary[[
        "sales_amount", "paid_amount", "sales_return", "customer_cashback",
        "executive_commission", "teamleader_commission", "gm_commission"
    ]].sum()
    st.success(
        f"**Total Sales:** {totals['sales_amount']:,.2f} | "
        f"**Total Deposit:** {totals['paid_amount']:,.2f} | "
        f"**Total Return:** {totals['sales_return']:,.2f} | "
        f"**Total Customer Cashback:** {totals['customer_cashback']:,.2f} | "
        f"**Total Executive Commission:** {totals['executive_commission']:,.2f} | "
        f"**Total Team Leader Commission:** {totals['teamleader_commission']:,.2f} | "
        f"**Total GM Commission:** {totals['gm_commission']:,.2f}|"
        #f" **Total Outstanding:** {filtered['customer_outstanding'].sum():,.2f} BDT"
    )

    # Optional: Download button for executive transaction summary
    output_exec_trans = BytesIO()
    summary.to_excel(output_exec_trans, index=False, engine='openpyxl')
    output_exec_trans.seek(0)
    st.download_button(
        label="Download Executive Transaction Summary as Excel",
        data=output_exec_trans,
        file_name=f"{selected_exec}_transaction_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="exec_trans_download"
    )


# 9. Executive Transaction (End)

# 10. Date wise sales summary (Start)
elif page == "🗓️ Date Summary":
    st.header("📅 Date-wise Sales Executive-wise Sales & Deposit Transactions")

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Date range selection
    min_date, max_date = df['date'].min(), df['date'].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date], key="datewise_sales")

    # Filter data by date range
    filtered = df[
        (df["date"] >= pd.to_datetime(date_range[0])) &
        (df["date"] <= pd.to_datetime(date_range[1]))
    ].copy()

    # Group by date and sales executive
    summary = filtered.groupby(
        [filtered["date"].dt.date, "sales_executive"]
    ).agg({
        "sales_amount": "sum",
        "paid_amount": "sum",
        "sales_return": "sum",
        "customer_cashback": "sum"
    }).reset_index().rename(columns={"date": "Date", "sales_executive": "Sales Executive"})

    st.subheader(f"Summary from {date_range[0]} to {date_range[1]}")
    st.dataframe(summary, use_container_width=True)

    # Show totals
    totals = summary[["sales_amount", "paid_amount", "sales_return", "customer_cashback"]].sum()
    st.success(
        f"**Total Sales:** {totals['sales_amount']:,.2f} | "
        f"**Total Deposit:** {totals['paid_amount']:,.2f} | "
        f"**Total Return:** {totals['sales_return']:,.2f} | "
        f"**Total Customer Cashback:** {totals['customer_cashback']:,.2f}"
    )

    # Download button for summary
    output_datewise = BytesIO()
    summary.to_excel(output_datewise, index=False, engine='openpyxl')
    output_datewise.seek(0)
    st.download_button(
        label="Download Date-wise Sales Summary as Excel",
        data=output_datewise,
        file_name=f"datewise_sales_summary_{date_range[0]}_{date_range[1]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="datewise_download"
    )


# 10. Date wise sales summary (End)

# 11. Customer Category-wise Transactions (Start)

elif page == "🏷️ Cust by Type":
    st.header("📅 Date Range & Customer Category-wise Sales, Deposit, Return & Commission")

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Select customer category
    if "customer_type" in df.columns:
        categories = df["customer_type"].dropna().unique()
        selected_category = st.selectbox("Select Customer Category", categories, key="cust_cat")
    else:
        st.warning("No 'customer_type' column found in data.")
        selected_category = None

    # Date range selection
    min_date, max_date = df['date'].min(), df['date'].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date], key="cust_cat_date")

    # Filter data by category and date range
    if selected_category is not None:
        filtered = df[
            (df["customer_type"] == selected_category) &
            (df["date"] >= pd.to_datetime(date_range[0])) &
            (df["date"] <= pd.to_datetime(date_range[1]))
        ].copy()

        # Group by customer
        summary = filtered.groupby("customer_name").agg({
            "sales_amount": "sum",
            "paid_amount": "sum",
            "sales_return": "sum",
            "customer_cashback": "sum",
            "executive_commission": "sum",
            "teamleader_commission": "sum",
            "gm_commission": "sum"
        }).reset_index()

        st.subheader(f"Summary for '{selected_category}' from {date_range[0]} to {date_range[1]}")
        st.dataframe(summary, use_container_width=True)

        # Show totals
        totals = summary[[
            "sales_amount", "paid_amount", "sales_return", "customer_cashback",
            "executive_commission", "teamleader_commission", "gm_commission"
        ]].sum()
        st.success(
            f"**Total Sales:** {totals['sales_amount']:,.2f} | "
            f"**Total Deposit:** {totals['paid_amount']:,.2f} | "
            f"**Total Return:** {totals['sales_return']:,.2f} | "
            f"**Total Customer Cashback:** {totals['customer_cashback']:,.2f} | "
            f"**Total Executive Commission:** {totals['executive_commission']:,.2f} | "
            f"**Total Team Leader Commission:** {totals['teamleader_commission']:,.2f} | "
            f"**Total GM Commission:** {totals['gm_commission']:,.2f}"
        )

        # Download button for summary
        output_cat = BytesIO()
        summary.to_excel(output_cat, index=False, engine='openpyxl')
        output_cat.seek(0)
        st.download_button(
            label="Download Category-wise Transactions as Excel",
            data=output_cat,
            file_name=f"{selected_category}_transactions_{date_range[0]}_{date_range[1]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="cat_download"
        )


# 11. Customer Category-wise Transactions (End)

# 12. Category-wise Transactions (Start)
elif page == "🗃️ Type Sales":
    st.header("📅 Date Range & Customer Category-wise Sales, Deposit, Return & Commission")

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Multi-select customer types
    if "customer_type" in df.columns:
        categories = df["customer_type"].dropna().unique()
        selected_categories = st.multiselect("Select Customer Type(s)", categories, default=list(categories), key="cust_cat_multi")
    else:
        st.warning("No 'customer_type' column found in data.")
        selected_categories = []

    # Date range selection
    min_date, max_date = df['date'].min(), df['date'].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date], key="cust_cat_date")

    # Filter data by selected customer types and date range
    if selected_categories:
        filtered = df[
            (df["customer_type"].isin(selected_categories)) &
            (df["date"] >= pd.to_datetime(date_range[0])) &
            (df["date"] <= pd.to_datetime(date_range[1]))
        ].copy()

        # Group by customer
        summary = filtered.groupby("customer_name").agg({
            "sales_amount": "sum",
            "paid_amount": "sum",
            "sales_return": "sum",
            "customer_cashback": "sum",
            "executive_commission": "sum",
            "teamleader_commission": "sum",
            "gm_commission": "sum"
        }).reset_index()

        st.subheader(f"Summary for {', '.join(selected_categories)} from {date_range[0]} to {date_range[1]}")
        st.dataframe(summary, use_container_width=True)

        # Executive-wise summary for selected customer types and date range
        st.markdown("### 🧑‍💼 Executive-wise Summary for Selected Customer Types")
        exec_summary = filtered.groupby("sales_executive").agg({
            "sales_amount": "sum",
            "paid_amount": "sum",
            "sales_return": "sum",
            "customer_cashback": "sum",
            "executive_commission": "sum",
            "teamleader_commission": "sum",
            "gm_commission": "sum"
        }).reset_index().rename(columns={"sales_executive": "Executive"})
        st.dataframe(exec_summary, use_container_width=True)

        # Show totals
        totals = summary[[
            "sales_amount", "paid_amount", "sales_return", "customer_cashback",
            "executive_commission", "teamleader_commission", "gm_commission"
        ]].sum()
        st.success(
            f"**Total Sales:** {totals['sales_amount']:,.2f} | "
            f"**Total Deposit:** {totals['paid_amount']:,.2f} | "
            f"**Total Return:** {totals['sales_return']:,.2f} | "
            f"**Total Customer Cashback:** {totals['customer_cashback']:,.2f} | "
            f"**Total Executive Commission:** {totals['executive_commission']:,.2f} | "
            f"**Total Team Leader Commission:** {totals['teamleader_commission']:,.2f} | "
            f"**Total GM Commission:** {totals['gm_commission']:,.2f}"
        )

        # Download button for summary
        output_cat = BytesIO()
        summary.to_excel(output_cat, index=False, engine='openpyxl')
        output_cat.seek(0)
        st.download_button(
            label="Download Category-wise Transactions as Excel",
            data=output_cat,
            file_name=f"category_transactions_{date_range[0]}_{date_range[1]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="cat_download"
        )

        # Download button for executive summary
        output_exec = BytesIO()
        exec_summary.to_excel(output_exec, index=False, engine='openpyxl')
        output_exec.seek(0)
        st.download_button(
            label="Download Executive-wise Summary as Excel",
            data=output_exec,
            file_name=f"executive_summary_{date_range[0]}_{date_range[1]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="exec_download")
        

# 12. Category-wise Transactions (End)

# 13. Daily Sales Summary (Start)

elif page == "📆 Daily Recap":
    st.header("📅 Daily Sales, Deposit, Return & Due Summary")

    # Always calculate customer_outstanding
    df["customer_outstanding"] = (
        df["openning_balance"].fillna(0) +
        df["sales_amount"].fillna(0) -
        df["sales_return"].fillna(0) -
        df["paid_amount"].fillna(0) -
        df["customer_cashback"].fillna(0)
    )

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Date range selection
    min_date, max_date = df['date'].min(), df['date'].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date], key="daily_sales")

    # Filter data by date range
    filtered = df[
        (df["date"] >= pd.to_datetime(date_range[0])) &
        (df["date"] <= pd.to_datetime(date_range[1]))
    ].copy()

    # --- Daily summary by date ---
    daily_summary = filtered.groupby(filtered["date"].dt.date).agg({
        "sales_amount": "sum",
        "paid_amount": "sum",
        "sales_return": "sum",
        "customer_cashback": "sum",
        "customer_outstanding": "sum"
    }).reset_index().rename(columns={"date": "Date"})

    st.subheader(f"Daily Summary from {date_range[0]} to {date_range[1]}")
    st.dataframe(daily_summary, use_container_width=True)

    # --- Customer-wise daily summary ---
    st.markdown("### 👤 Customer-wise Daily Summary")
    cust_daily = filtered.groupby([filtered["date"].dt.date, "customer_name"]).agg({
        "sales_amount": "sum",
        "paid_amount": "sum",
        "sales_return": "sum"
    }).reset_index().rename(columns={"date": "Date", "customer_name": "Customer"})
    st.dataframe(cust_daily, use_container_width=True)

    # --- Executive-wise daily summary ---
    st.markdown("### 🧑‍💼 Executive-wise Daily Summary")
    exec_daily = filtered.groupby([filtered["date"].dt.date, "sales_executive"]).agg({
        "sales_amount": "sum",
        "paid_amount": "sum",
        "sales_return": "sum"
    }).reset_index().rename(columns={"date": "Date", "sales_executive": "Executive"})
    st.dataframe(exec_daily, use_container_width=True)

    # Show totals
    totals = daily_summary[["sales_amount", "paid_amount", "sales_return", "customer_cashback", "customer_outstanding"]].sum()
    st.success(
        f"**Total Sales:** {totals['sales_amount']:,.2f} | "
        f"**Total Deposit:** {totals['paid_amount']:,.2f} | "
        f"**Total Return:** {totals['sales_return']:,.2f} | "
        f"**Total Cashback:** {totals['customer_cashback']:,.2f} | "
        f"**Total Due:** {totals['customer_outstanding']:,.2f}"
    )

    # Daily sales and deposit line chart
    st.markdown("### 📈 Daily Sales & Deposit Trend")
    fig_comm = px.line(
        daily_summary,
        x="Date",
        y=["sales_amount", "paid_amount"],
        markers=True,
        labels={"value": "Amount", "Date": "Date", "variable": "Type"},
        title="Daily Sales & Deposit Trend"
    )
    st.plotly_chart(fig_comm, use_container_width=True)

    # Download buttons
    output_daily = BytesIO()
    daily_summary.to_excel(output_daily, index=False, engine='openpyxl')
    output_daily.seek(0)
    st.download_button(
        label="Download Daily Sales Summary as Excel",
        data=output_daily,
        file_name=f"daily_sales_summary_{date_range[0]}_{date_range[1]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="daily_download"
    )

    output_cust = BytesIO()
    cust_daily.to_excel(output_cust, index=False, engine='openpyxl')
    output_cust.seek(0)
    st.download_button(
        label="Download Customer-wise Daily Summary as Excel",
        data=output_cust,
        file_name=f"customer_daily_summary_{date_range[0]}_{date_range[1]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="cust_daily_download"
    )

    output_exec = BytesIO()
    exec_daily.to_excel(output_exec, index=False, engine='openpyxl')
    output_exec.seek(0)
    st.download_button(
        label="Download Executive-wise Daily Summary as Excel",
        data=output_exec,
        file_name=f"executive_daily_summary_{date_range[0]}_{date_range[1]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="exec_daily_download"
    )
    

# 13. Daily Sales Summary (End)

# 14. About Us (Start)


elif page == "💡 About":
    st.title("💼 About Us")
    st.markdown("---")

    # Company logo
    logo = Image.open("logo.png")
    st.image(logo, width=150, caption="WELBURG METAL PVT LTD")

    st.subheader("🏢 Company Overview")
    st.markdown("""
**WELBURG METAL PVT LTD** is a Bangladesh-based company focused on delivering high-quality **All kinds of kitchenware and cockware importer and manufucrar**. We are committed to excellence, durability, and customer satisfaction across all our operations.
    """)

    st.subheader("📍 Company Details")
    st.markdown("""
- **Name:** WELBURG METAL PVT LTD  
- **Address:** Sadapur, Nagorkonda, Savar, Dhaka, Bangladesh  
- **Contact:** 01787933422  
- **Email:** welburgmetal2021@gmail.com
    """)

    st.subheader("👨‍💼 Owner Information")

    # Managing Director photo
    md_pic = Image.open("md_pic.jpg")
    st.image(md_pic, width=150, caption="Md. Hasanuzzaman Helal")

    st.markdown("""
- **Name:** Md. Hasanuzzaman Helal  
- **Position:** Managing Director  
- **Contact:** 01958385999  
- **Email:** hazanuzzaman@welburgmetal.com
    """)

    st.subheader("🛠️ Our Products")
    st.markdown("""
We specialize in:
- All kinds of cock and kitchenware Products
- Customized metal solutions (as per demand)
- Industrial-grade cookware and accessories
    """)

    st.subheader("🎯 Our Mission")
    st.markdown("To be a reliable leader in the steel industry, providing top-quality products and services that exceed customer expectations.")

    st.subheader("🌱 Our Vision")
    st.markdown("To support Bangladesh's industrial growth through innovation, quality, and long-term partnerships.")

    st.subheader("🤝 Get in Touch")
    st.markdown("We welcome your queries, suggestions, and partnership opportunities. Let’s build the future together!")

    
# 14. About Us (End)

# 15. Sales & Deposit performance (Start)
elif page == "📈 Performance":
    st.title("📈 Executive & Customer Performance Statistics")
    st.markdown("---")

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Date range selection
    min_date, max_date = df['date'].min(), df['date'].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date], key="performance_date")

    # Filter data by date range
    filtered = df[
        (df["date"] >= pd.to_datetime(date_range[0])) &
        (df["date"] <= pd.to_datetime(date_range[1]))
    ].copy()

    # --- Executive Performance Bar Chart ---
    st.markdown("### 🧑‍💼 Executive-wise Sales & Deposit (Bar Chart)")
    exec_perf = filtered.groupby("sales_executive").agg({
        "sales_amount": "sum",
        "paid_amount": "sum",
        "sales_return": "sum"
    }).reset_index().rename(columns={"sales_executive": "Executive"})
    fig_exec = px.bar(
        exec_perf,
        x="Executive",
        y=["sales_amount", "paid_amount", "sales_return"],
        barmode="group",
        labels={"value": "Amount", "variable": "Type"},
        title="Executive-wise Sales, Deposit & Return"
    )
    st.plotly_chart(fig_exec, use_container_width=True)

    # --- Customer Performance Bar Chart ---
    st.markdown("### 👤 Top 10 Customers by Sales (Bar Chart)")
    cust_perf = filtered.groupby("customer_name")["sales_amount"].sum().reset_index().sort_values(by="sales_amount", ascending=False).head(10)
    fig_cust = px.bar(
        cust_perf,
        x="customer_name",
        y="sales_amount",
        labels={"customer_name": "Customer", "sales_amount": "Sales Amount"},
        title="Top 10 Customers by Sales"
    )
    st.plotly_chart(fig_cust, use_container_width=True)

    # --- Executive Sales Trend Line Chart ---
    st.markdown("### 📈 Executive-wise Sales Trend (Line Chart)")
    exec_trend = filtered.groupby([filtered["date"].dt.to_period('M').astype(str), "sales_executive"])["sales_amount"].sum().reset_index()
    fig_exec_trend = px.line(
        exec_trend,
        x="date",
        y="sales_amount",
        color="sales_executive",
        markers=True,
        labels={"date": "Month", "sales_amount": "Sales Amount", "sales_executive": "Executive"},
        title="Executive-wise Monthly Sales Trend"
    )
    st.plotly_chart(fig_exec_trend, use_container_width=True)

    # --- Customer Sales Trend Line Chart ---
    st.markdown("### 📈 Top 5 Customers Sales Trend (Line Chart)")
    top5_customers = cust_perf["customer_name"].head(5).tolist()
    cust_trend = filtered[filtered["customer_name"].isin(top5_customers)]
    cust_trend = cust_trend.groupby([cust_trend["date"].dt.to_period('M').astype(str), "customer_name"])["sales_amount"].sum().reset_index()
    fig_cust_trend = px.line(
        cust_trend,
        x="date",
        y="sales_amount",
        color="customer_name",
        markers=True,
        labels={"date": "Month", "sales_amount": "Sales Amount", "customer_name": "Customer"},
        title="Top 5 Customers Monthly Sales Trend"
    )
    st.plotly_chart(fig_cust_trend, use_container_width=True)

# 15. Sales & Deposit performance (End)

# 16. About data analyst (Start)
elif page == "👨‍💻 Analyst Bio":
    st.title("📊 About Data Analyst")
    st.write("""
A **Data Analyst** is a professional who collects, processes, and analyzes data to help organizations make informed decisions.

As a **Data Analyst**, I work with raw data, clean and transform it, then generate insights through reports, dashboards, and visualizations.

#### 🔍 Responsibilities:
- Gathering data from various sources (e.g., Excel, databases, APIs)
- Cleaning and preprocessing data using Python or tools like Excel
- Using tools like **Pandas**, **NumPy**, **Google Sheets**, or **SQL**
- Creating reports, dashboards, and visual insights using **Streamlit**, **Plotly**, or **Matplotlib**
- Supporting business decisions with data-driven insights

#### 🧠 Key Tools I Use:
- **Python** – Core language for data manipulation
- **Pandas & NumPy** – Data wrangling and computation
- **Streamlit** – Interactive dashboards
- **Google Sheets** – Simple but powerful analytics
- **SQL** – Querying structured data
- **Plotly / Seaborn / Matplotlib** – For stunning visualizations

#### 💡 My Experience:
With experience in **pharmacy, inventory, and sales data**, I specialize in turning raw business data into easy-to-understand dashboards and reports for decision-makers.

Whether it's **tracking sales**, **managing customer dues**, or **monitoring executive performance**, I bring real-world data into action.

    """)

    st.success("Let data talk, and let businesses grow smarter with insights!")


# 16. About data analyst (End)

# 17. Sales commission (Start)
elif page == "💸 Commissions":
    st.title("💸 Date Range Wise Executive, Team Leader & GM Commission")
    st.markdown("---")

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Date range selection
    min_date, max_date = df['date'].min(), df['date'].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date], key="commission_date")

    # Filter data by date range
    filtered = df[
        (df["date"] >= pd.to_datetime(date_range[0])) &
        (df["date"] <= pd.to_datetime(date_range[1]))
    ].copy()

    # Group by executive and show commission summary
    st.markdown("### 🧑‍💼 Executive-wise Commission Summary")
    exec_comm = filtered.groupby("sales_executive").agg({
        "executive_commission": "sum",
        "teamleader_commission": "sum",
        "gm_commission": "sum"
    }).reset_index().rename(columns={
        "sales_executive": "Executive",
        "executive_commission": "Executive Commission",
        "teamleader_commission": "Team Leader Commission",
        "gm_commission": "GM Commission"
    })
    st.dataframe(exec_comm, use_container_width=True)

    # Show totals
    totals = exec_comm[["Executive Commission", "Team Leader Commission", "GM Commission"]].sum()
    st.success(
        f"**Total Executive Commission:** {totals['Executive Commission']:,.2f} | "
        f"**Total Team Leader Commission:** {totals['Team Leader Commission']:,.2f} | "
        f"**Total GM Commission:** {totals['GM Commission']:,.2f}"
    )

    

    # Download button for commission summary
    output_comm = BytesIO()
    exec_comm.to_excel(output_comm, index=False, engine='openpyxl')
    output_comm.seek(0)
    st.download_button(
        label="Download Commission Summary as Excel",
        data=output_comm,
        file_name=f"commission_summary_{date_range[0]}_{date_range[1]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="commission_download"
    )

# 17. Sales commission (End)
elif page == "🛒 Products":
    st.title("📊 Our product prices")
    st.markdown("---")
   

    st.markdown("### 🏷️ Product Information")

    import pandas as pd

    # WITHOUT LID
    st.markdown("#### WITHOUT LID")
    data_without_lid = [
        ["FRYPAN", "16cm", "535.00", "0.00", ""],
        ["FRYPAN", "20cm", "800.00", "0.00", ""],
        ["FRYPAN", "24cm", "0.00", "1,110.00", ""],
        ["FRYPAN", "26cm", "1,185.00", "1,240.00", ""],
        ["FRYPAN", "28cm", "1,315.00", "1,370.00", ""],
        ["FRYPAN", "30cm", "1,530.00", "1,585.00", ""],
        ["DEEP FRYPAN", "26cm", "0.00", "1,450.00", ""],
        ["DEEP FRYPAN", "28cm", "0.00", "1,600.00", ""],
        ["CASSEROLE", "28cm", "1,850.00", "0.00", ""],
        ["KARAI", "28cm", "1,580.00", "0.00", ""],
        ["WOKPAN", "28cm", "1,420.00", "0.00", ""],
    ]
    df_without_lid = pd.DataFrame(data_without_lid, columns=["Item Name", "Size", "Regular Price", "Premium Price", "Remarks"])
    st.dataframe(df_without_lid, use_container_width=True)

    # WITH LID
    st.markdown("#### WITH LID")
    data_with_lid = [
        ["FRYPAN", "20cm", "965.00", "0.00", ""],
        ["FRYPAN", "24cm", "0.00", "1,290.00", ""],
        ["FRYPAN", "26cm", "1,370.00", "1,420.00", ""],
        ["FRYPAN", "28cm", "1,490.00", "1,550.00", ""],
        ["FRYPAN", "30cm", "1,710.00", "1,765.00", ""],
        ["DEEP FRYPAN", "26cm", "0.00", "1,640.00", ""],
        ["DEEP FRYPAN", "28cm", "0.00", "1,800.00", ""],
        ["CASSEROLE", "28cm", "2,020.00", "0.00", ""],
        ["KARAI", "28cm", "1,760.00", "0.00", ""],
        ["WOKPAN", "28cm", "1,600.00", "0.00", ""],
    ]
    df_with_lid = pd.DataFrame(data_with_lid, columns=["Item Name", "Size", "Regular Price", "Premium Price", "Remarks"])
    st.dataframe(df_with_lid, use_container_width=True)

    # OTHERS
    st.markdown("#### OTHERS")
    data_others = [
        ["ROTI TAWA", "26cm", "1,070.00", "0.00", ""],
        ["DOSHA TAWA", "28cm", "1,170.00", "0.00", ""],
        ["GRILLPAN", "28*22cm", "2,000.00", "0.00", ""],
    ]
    df_others = pd.DataFrame(data_others, columns=["Item Name", "Size", "Regular Price", "Premium Price", "Remarks"])
    st.dataframe(df_others, use_container_width=True)

    # LID
    st.markdown("#### LID")
    data_lid = [
        ["LID WITH KNOB", "20cm", "200", "", "NO DISCOUNT"],
        ["LID WITH KNOB", "24cm", "300", "", "NO DISCOUNT"],
        ["LID WITH KNOB", "26cm", "300", "", "NO DISCOUNT"],
        ["LID WITH KNOB", "28cm", "300", "", "NO DISCOUNT"],
        ["LID WITH KNOB", "30cm", "350", "", "NO DISCOUNT"],
    ]
    df_lid = pd.DataFrame(data_lid, columns=["Item Name", "Size", "Regular Price", "Premium Price", "Remarks"])
    st.dataframe(df_lid, use_container_width=True)
    

st.markdown("---")


st.markdown(
    """
    <div style='text-align: center; font-size: 15px;'>
        <b>Developed & Maintained by:</b> Mujakkir Ahmad<br>
        Accountant | Data Analyst<br>
        WELBURG METAL PVT LTD<br>
        Sadapur, Nagorkonda, Savar, Dhaka, Bangladesh<br>
        <b>Contact:</b> 01787933422<br>
        <b>Email:</b> mujakkirar4@gmail.com<br>
        <br>
        &copy; 2025 WELBURG METAL PVT LTD. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)

