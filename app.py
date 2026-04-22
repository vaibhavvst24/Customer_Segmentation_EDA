import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Customer Sales Segmentation",
    page_icon="🧑🏻",
    layout="wide"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
    <style>
        .main {
            background-color: #0E1117;
        }
        .stMetric {
            background-color: #1c1f26;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    .stApp {
        font-family: 'Poppins', sans-serif;
    }

    h1 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🧑🏻Customer Sales Dashboard 📊</h1>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Custmer_sales.csv", encoding='ISO-8859-1')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='mixed', errors='coerce')
    df.dropna(inplace=True)
    # Reduce memory usage
    df['Country'] = df['Country'].astype('category')
    df['Description'] = df['Description'].astype('category')
    
    return df

df = load_data()
# Safe sampling (prevents crash)
if len(df) > 2000:
    df = df.sample(2000, random_state=42)


# ------------------ SIDEBAR ------------------
st.sidebar.header("🔍 Filters")

country = st.sidebar.multiselect(
    "Select Country",
    options=df['Country'].unique(),
    default=df['Country'].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['InvoiceDate'].min(), df['InvoiceDate'].max()]
)

# Filter Data
filtered_df = df[
    (df['Country'].isin(country)) &
    (df['InvoiceDate'].dt.date >= date_range[0]) &
    (df['InvoiceDate'].dt.date <= date_range[1])
]

# ------------------ KPI METRICS ------------------
total_sales = (filtered_df['Quantity'] * filtered_df['UnitPrice']).sum()
total_orders = filtered_df['InvoiceNo'].nunique()
total_customers = filtered_df['CustomerID'].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Sales", f"${total_sales:,.2f}", delta="+5%")
col2.metric("🧾 Total Orders", total_orders, delta="-2%")
col3.metric("👥 Customers", total_customers, delta="+3%")

def center_title(fig):
    fig.update_layout(title_x=0.5)
    return fig

# ------------------ CHARTS ------------------

# 1. Sales by Country
st.markdown("<h3 style='text-align: center;'>🌍 Sales by Country</h3>", unsafe_allow_html=True)
country_sales = filtered_df.groupby('Country')['Quantity'].sum().nlargest(10).reset_index()

fig1 = px.bar(
    country_sales,
    x='Country',
    y='Quantity',
    color='Quantity',
    template='plotly_dark'
)

st.plotly_chart(center_title(fig1), use_container_width=True)
st.markdown("<p style='text-align: center;'>This chart shows the Overall Sales completed in Every Country.</p>", unsafe_allow_html=True)

# Total Products
st.markdown("<h3 style='text-align: center;'>Top Products</h3>", unsafe_allow_html=True)
df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
top_products = (
    df.groupby("Description")[["TotalPrice","Quantity","UnitPrice"]]
    .sum()
    .sort_values(ascending=False, by=['Quantity','UnitPrice'])
    .head(10)
)

tp = pd.DataFrame(top_products)
tp
st.markdown("<p style='text-align: center;'>This Table Shows the Top Products Sold with there appropriate quantity as well as unit price</p>", unsafe_allow_html=True)

# Daily Sales 
st.markdown("<h3 style='text-align: center;'>Daily Sales</h3>", unsafe_allow_html=True)
daily_sales = (
    df.groupby(df["InvoiceDate"].dt.date)["TotalPrice"].sum()
)

ds = pd.DataFrame(daily_sales)
ds
st.markdown("<p style='text-align: center;'>This Table Shows the Daily Sales of everyday with the total price.</p>", unsafe_allow_html=True)


# -------------------------------------------------------------------------------------------------------------
# 2. Top Products
st.markdown("<h3 style='text-align: center;'>Top 10 Products</h3>", unsafe_allow_html=True)
top_products = filtered_df.groupby('Description')['Quantity'].sum().nlargest(10).reset_index()

fig2 = px.bar(
    top_products,
    x='Quantity',
    y='Description',
    title="Top Products",
    orientation='h',
    color='Quantity',
    template='plotly_dark'
)
st.plotly_chart(center_title(fig2), use_container_width=True)
st.markdown("<p style='text-align: center;'>This chart shows the top products that have generated more revenue for the business.</p>", unsafe_allow_html=True)

# Top Expensive products
st.markdown("<h3 style='text-align: center;'>Top Expensive Products</h3>", unsafe_allow_html=True)
expensive_products = (
    df.groupby("Description")["UnitPrice"]
    .max()
    .sort_values(ascending=False)
    .head(10)
)

ep = pd.DataFrame(expensive_products)
ep
st.markdown("<p style='text-align: center;'>This Table Shows the Top Expensive Products in the Market with there Unit Price.</p>", unsafe_allow_html=True)

# 3. Sales Over Time
st.markdown("<h3 style='text-align: center;'>Sales Over Time </h3>", unsafe_allow_html=True)
filtered_df['Date'] = filtered_df['InvoiceDate'].dt.date
time_sales = filtered_df.groupby('Date')['Quantity'].sum().reset_index()

fig3 = px.line(
    time_sales,
    x='Date',
    y='Quantity',
    title="Sales Over Time",
    markers=True,
    template='plotly_dark'
)
st.plotly_chart(center_title(fig3), use_container_width=True)
st.markdown("<p style='text-align: center;'>This chart shows total revenue contribution from each country, helping identify top-performing markets.</p>", unsafe_allow_html=True)

# Monthly Sales 
st.markdown("<h3 style='text-align: center;'>Monthly Sales</h3>", unsafe_allow_html=True)
monthly_sales = (
    df.groupby(df["InvoiceDate"].dt.to_period("M"))["TotalPrice"]
    .sum()
)
ms = pd.DataFrame(monthly_sales)
ms
st.markdown("<p style='text-align: center;'>This Table Shows the Monthly Sales over a 30 day period of time.</p>", unsafe_allow_html=True)

# Top Sales per Invoice
st.markdown("<h3 style='text-align: center;'>Top Sales per Invoice</h3>", unsafe_allow_html=True)
invoice_sales = (
    df.groupby("InvoiceNo")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
ps = pd.DataFrame(invoice_sales)
ps
st.markdown("<p style='text-align: center;'>This Table Shows the Top Sales as per the Invoice Number of the Customer.</p>", unsafe_allow_html=True)

# 4. Price vs Quantity
st.markdown("<h3 style='text-align: center;'>💰 Price vs Quantity</h3>", unsafe_allow_html=True)

fig4 = px.scatter(
    filtered_df,
    x='UnitPrice',
    y='Quantity',
    title="Price vs Quantity",
    color='Country',
    template='plotly_dark'
)
st.plotly_chart(center_title(fig4), use_container_width=True)
st.markdown("<p style='text-align: center;'>This chart shows total revenue contribution from each country, helping identify top-performing markets.</p>", unsafe_allow_html=True)

# Average Order Value
st.markdown("<h3 style='text-align: center;'>Average Order Value</h3>", unsafe_allow_html=True)
avg_order_value = (
    df.groupby("CustomerID")["TotalPrice"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

aov = pd.DataFrame(avg_order_value)
aov

# High Quantity Purchase 
st.markdown("<h3 style='text-align: center;'>High Quantity Purchase</h3>", unsafe_allow_html=True)
high_quantity_customers = (
    df.groupby("CustomerID")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

hqc = pd.DataFrame(high_quantity_customers)
hqc

# 5. Quantity Distribution
st.markdown("<h3 style='text-align: center;'>📦 Quantity Distribution</h3>", unsafe_allow_html=True)

fig5 = px.histogram(
    filtered_df,
    x='Quantity',
    title="Quantity Distribution",
    nbins=50,
    template='plotly_dark'
)

st.plotly_chart(center_title(fig5), use_container_width=True)
st.markdown("<p style='text-align: center;'>This chart shows total revenue contribution from each country, helping identify top-performing markets.</p>", unsafe_allow_html=True)

# Top Quality Products
st.markdown("<h3 style='text-align: center;'>Top Quantity Products</h3>", unsafe_allow_html=True)
top_quantity_products = (
    df.groupby("Description")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

tqp = pd.DataFrame(top_quantity_products)
tqp
st.markdown("<p style='text-align: center;'>This Table Shows the Top Quantity Products that has been purchased in high quantity</p>", unsafe_allow_html=True)


# 6. Revenue by country
st.markdown("<h3 style='text-align: center;'>Revenue by Country</h3>", unsafe_allow_html=True)
filtered_df['Revenue'] = filtered_df['Quantity'] * filtered_df['UnitPrice']
country_rev = filtered_df.groupby('Country')['Revenue'].sum().reset_index()

fig6 = px.bar(
    country_rev,
    x='Country',
    y='Revenue',
    color='Revenue',
    title="Revenue by Country",
    color_continuous_scale='Blues',
    template='plotly_dark'
)
st.plotly_chart(fig6, use_container_width=True)
st.markdown("<p style='text-align: center;'>This chart shows total revenue contribution from each country, helping identify top-performing markets.</p>", unsafe_allow_html=True)

# Country Sales
st.markdown("<h3 style='text-align: center;'>Country Sales</h3>", unsafe_allow_html=True)
country_sales = (
    df.groupby("Country")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
)
cs = pd.DataFrame(country_sales)
cs
st.markdown("<p style='text-align: center;'>This table shows the number of sales done by countries as per the total price.</p>", unsafe_allow_html=True)

# Top Countries by Number of Orders
st.markdown("<h3 style='text-align: center;'>Top Countries by Number of Orders</h3>", unsafe_allow_html=True)
country_orders = (
    df.groupby("Country")["InvoiceNo"]
    .nunique()
    .sort_values(ascending=False)
)

co = pd.DataFrame(country_orders)
co
st.markdown("<p style='text-align: center;'>This table shows the Top countries with maximum number of Orders.</p>", unsafe_allow_html=True)

# Revenue Contribution by top 5 country
st.markdown("<h3 style='text-align: center;'>Revenue Generation of each country</h3>", unsafe_allow_html=True)
top_countries = (
    df.groupby("Country")["TotalPrice"]
    .sum()
    .nlargest(5)
)

tc = pd.DataFrame(top_countries)
tc
st.markdown("<p style='text-align: center;'>This table shows the Revenue Generation of top 5 countries.</p>", unsafe_allow_html=True)

# 7. Monthly Sales Trend
st.markdown("<h3 style='text-align: center;'>Monthly Sales Trend</h3>", unsafe_allow_html=True)
filtered_df['Month'] = filtered_df['InvoiceDate'].dt.to_period('M').astype(str)
monthly_sales = filtered_df.groupby('Month')['Revenue'].sum().reset_index()

fig7 = px.line(
    monthly_sales,
    x='Month',
    y='Revenue',
    markers=True,
    title="Monthly Revenue Trend",
    color_discrete_sequence=['#00FFFF'],
    template='plotly_dark'
)

st.plotly_chart(fig7, use_container_width=True)
st.markdown("<p style='text-align: center;'>Displays how revenue changes over time on a monthly basis, useful for trend and seasonality analysis.</p>", unsafe_allow_html=True)

# 8. Top Customers
st.markdown("<h3 style='text-align: center;'>Top Customers</h3>", unsafe_allow_html=True)
top_customers = filtered_df.groupby('CustomerID')['Revenue'].sum().nlargest(10).reset_index()

fig8 = px.bar(
    top_customers,
    x='CustomerID',
    y='Revenue',
    color='Revenue',
    title="Top 10 Customers by Revenue",
    color_continuous_scale='Inferno',
    template='plotly_dark'
)

st.plotly_chart(fig8, use_container_width=True)
st.markdown("<p style='text-align: center;'>Highlights the most valuable customers contributing the highest revenue.</p>", unsafe_allow_html=True)

# Customer with Highest Purchase Frequency
st.markdown("<h3 style='text-align: center;'>Customer with Highest Purchase Frequency</h3>", unsafe_allow_html=True)
frequency = (
    df.groupby("CustomerID")["InvoiceNo"]
    .nunique()
    .sort_values(ascending=False)
)

fr = pd.DataFrame(frequency)
fr
st.markdown("<p style='text-align: center;'>This table shows the Customers with highest purchase frequency who purchased in high quantites.</p>", unsafe_allow_html=True)

# Customers with Highest Monetary Value
st.markdown("<h3 style='text-align: center;'>Customers with Highest Monetary Value</h3>", unsafe_allow_html=True)
monetary = (
    df.groupby("CustomerID")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
)

mt = pd.DataFrame(monetary)
mt
st.markdown("<p style='text-align: center;'>This table shows the Customers with Highest Monetary Values.</p>", unsafe_allow_html=True)

# Customers with highest average order value
st.markdown("<h3 style='text-align: center;'>Customers with Highest Average order value</h3>", unsafe_allow_html=True)
avg_order_value = (
    df.groupby("CustomerID")["TotalPrice"]
    .mean()
    .sort_values(ascending=False)
)

aov = pd.DataFrame(avg_order_value)
aov
st.markdown("<p style='text-align: center;'>This table shows the Customers with the highest average order values.</p>", unsafe_allow_html=True)

# Customers Buying the Most products
st.markdown("<h3 style='text-align: center;'>Customers purchased the most products</h3>", unsafe_allow_html=True)
top_quantity_customers = (
    df.groupby("CustomerID")["Quantity"]
    .sum()
    .sort_values(ascending=False)
)

tqc = pd.DataFrame(top_quantity_customers)
tqc
st.markdown("<p style='text-align: center;'>Highlights the most valuable customers contributing the highest revenue.</p>", unsafe_allow_html=True)

# Customer with Longest Relationship
st.markdown("<h3 style='text-align: center;'>Top Customers</h3>", unsafe_allow_html=True)
customer_lifetime = (
    df.groupby("CustomerID")["InvoiceDate"]
    .agg(["min", "max"])
)
customer_lifetime["LifetimeDays"] = (
    customer_lifetime["max"] - customer_lifetime["min"]
).dt.days

customer_lifetime.sort_values("LifetimeDays", ascending=False).head()

monthly_frequency = (
    df.groupby(["CustomerID", df["InvoiceDate"].dt.to_period("M")])["InvoiceNo"]
    .nunique()
)

mf = monthly_frequency.sort_values(ascending=False).head()
mf1 = pd.DataFrame(mf)
mf1
st.markdown("<p style='text-align: center;'>Highlights the most valuable customers contributing the highest revenue.</p>", unsafe_allow_html=True)

# 9. Order Distribution by Country
st.markdown("<h3 style='text-align: center;'>Order Distribution by Country</h3>", unsafe_allow_html=True)
df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
country_sales = df.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False).head(5)

fig9 = px.pie(
    values=country_sales.values,
    names=country_sales.index,
    title="Most Sales Distribution by Country",
    color_discrete_sequence=px.colors.sequential.Agsunset
)

fig9.update_traces(
    textinfo="percent+label",
    pull=[0.05]*len(country_sales),
    marker_line_width=1, marker_line_color='white'
)

fig9.update_layout(
    template="plotly_dark",
    height=550,
    width=1100
)
st.plotly_chart(fig9, use_container_width=True)
st.markdown("<p style='text-align: center;'>Represents the proportion of total orders placed from each country.</p>", unsafe_allow_html=True)

# Average Spending by country
st.markdown("<h3 style='text-align: center;'>Average Spending by country</h3>", unsafe_allow_html=True)
avg_country_spending = (
    df.groupby("Country")["TotalPrice"]
    .mean()
    .sort_values(ascending=False)
)

acs = pd.DataFrame(avg_country_spending)
acs
st.markdown("<p style='text-align: center;'>This table shows the average spending of countries on a particular product.</p>", unsafe_allow_html=True)

# 10. Unit Price Distribution
st.markdown("<h3 style='text-align: center;'>Unit Price Distribution</h3>", unsafe_allow_html=True)
fig10 = px.box(
    filtered_df,
    y='UnitPrice',
    title="Unit Price Distribution",
    color_discrete_sequence=['#FFA500'],
    template='plotly_dark'
)

st.plotly_chart(fig10, use_container_width=True)
st.markdown("<p style='text-align: center;'>Shows the spread and outliers in product pricing, helping detect anomalies or pricing strategy.</p>", unsafe_allow_html=True)

# ------------------ DATA PREVIEW ------------------
st.markdown("<h3 style='text-align: center;'>📄 Dataset Preview</h3>", unsafe_allow_html=True)
st.dataframe(filtered_df.head())

# ------------------ FOOTER ------------------
st.markdown(
    "<h4 style='text-align: center;'>🚀 Built with Streamlit & Plotly | Interactive EDA Dashboard</h4>",
    unsafe_allow_html=True
)