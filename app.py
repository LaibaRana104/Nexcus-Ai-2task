# ---------------------------------------------------
# 📌 Task 2: Interactive Dashboard (Retail Data)
# ---------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_excel("Online_Retail.xlsx")
    df.drop_duplicates(inplace=True)
    df = df.dropna(subset=["CustomerID"])
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔎 Filters")
country = st.sidebar.selectbox("Select Country", options=df["Country"].unique())
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["InvoiceDate"].min(), df["InvoiceDate"].max()]
)

# Apply filters
df_filtered = df[
    (df["Country"] == country) &
    (df["InvoiceDate"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# Main Title & Intro
st.title("📊 Customer Insights Dashboard")
st.markdown("""
This dashboard provides an overview of **GlobalMart sales performance**.  
Use the filters on the left to explore sales by **country and date range**.
""")

# Handle case when no data
if df_filtered.empty:
    st.warning("⚠️ No data available for the selected filters. Try changing country or date range.")
else:
    # KPIs
    total_revenue = df_filtered["TotalPrice"].sum()
    total_orders = df_filtered["InvoiceNo"].nunique()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("💰 Total Revenue", f"£{total_revenue:,.0f}")
    kpi2.metric("🛒 Total Orders", total_orders)
    kpi3.metric("📦 Avg Order Value", f"£{avg_order_value:,.2f}")

    # Daily revenue
    daily_sales = df_filtered.resample("D", on="InvoiceDate")["TotalPrice"].sum().reset_index()
    fig1 = px.line(daily_sales, x="InvoiceDate", y="TotalPrice", title="📈 Daily Revenue Trend")
    st.plotly_chart(fig1, use_container_width=True)

    # Top products
    top_products = df_filtered.groupby("Description")["TotalPrice"].sum().sort_values(ascending=False).head(10).reset_index()
    fig2 = px.bar(top_products, x="TotalPrice", y="Description", orientation="h", title="🏆 Top 10 Products by Revenue")
    st.plotly_chart(fig2, use_container_width=True)

    # Revenue by weekday
    df_filtered["Weekday"] = df_filtered["InvoiceDate"].dt.day_name()
    weekday_rev = df_filtered.groupby("Weekday")["TotalPrice"].sum().reindex(
        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]).reset_index()
    fig3 = px.bar(weekday_rev, x="Weekday", y="TotalPrice", title="📅 Revenue by Weekday")
    st.plotly_chart(fig3, use_container_width=True)

# Revenue by country (overall, full dataset)
country_rev = df.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False).head(10).reset_index()
fig4 = px.bar(country_rev, x="Country", y="TotalPrice", title="🌍 Top 10 Countries by Revenue")
st.plotly_chart(fig4, use_container_width=True)
