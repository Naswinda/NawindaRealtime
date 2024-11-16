import streamlit as st
import pandas as pd
from pinotdb import connect
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh 

# Set up page layout
st.set_page_config(layout="wide")
st_autorefresh(interval=5000)

# Add custom CSS for title and subtitle color
st.markdown("""
    <style>
        .title {
            font-size: 48px;
            font-weight: bold;
            color: #FF6347;  /* Change title color to Tomato */
            text-align: center;
        }
        .subheader {
            font-size: 24px;
            font-weight: bold;
            color: #32CD32;  /* Change subtitle color to LimeGreen */
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Title and subtitle
st.markdown('<p class="title">NANAS ARTTOYS 🧸</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">- The Art of Play -</p>', unsafe_allow_html=True)

# Establish connection
conn = connect(host='54.179.164.123', port=8099, path='/query/sql', schema='http')
curs = conn.cursor()

# Row 1 - Column 1: Total Sales by Country (Choropleth Map)
curs.execute('''
SELECT
  COUNTRY,
  SUM(TOTAL_PRICE) AS totalSales
FROM 5_join_group
GROUP BY COUNTRY
ORDER BY totalSales DESC;
''')
tables = [row for row in curs.fetchall()]
df_country = pd.DataFrame(tables, columns=['COUNTRY', 'totalSales'])

# Map country names to ISO-3166-1 alpha-3 codes
country_map = {
    'Thailand': 'THA',
    'China': 'CHN',
    'Singapore': 'SGP',
    'Hong Kong': 'HKG',
    'Japan': 'JPN',
    'Malaysia': 'MYS',
    'Korea': 'KOR',
    'Vietnam': 'VNM',
    'Australia': 'AUS'
}
df_country['COUNTRY_CODE'] = df_country['COUNTRY'].map(country_map)

fig_country = px.choropleth(
    df_country,
    locations='COUNTRY_CODE',
    color='totalSales',
    hover_name='COUNTRY',
    color_continuous_scale='Viridis',
    title='Total Sales by Country',
    template="plotly_dark"
)

# Row 1 - Column 2: Total Quantity and Sales by Product Type (Table)
curs.execute('''
SELECT
  TYPE,
  SUM(QUANTITY) AS totalQuantity,
  SUM(TOTAL_PRICE) AS totalSales
FROM 5_join_group
GROUP BY TYPE
ORDER BY totalQuantity DESC;
''')
tables = [row for row in curs.fetchall()]
df_product = pd.DataFrame(tables, columns=['TYPE', 'totalQuantity', 'totalSales'])
df_product['totalSales'] = df_product['totalSales'].apply(lambda x: f"{x:.2f}")

fig_product = go.Figure(data=[go.Table(
    header=dict(
        values=["Product Type", "Total Quantity", "Total Sales"],
        fill=dict(color='#4CAF50'),
        align='center',
        font=dict(color='white', size=14),
    ),
    cells=dict(
        values=[df_product['TYPE'], df_product['totalQuantity'], df_product['totalSales']],
        fill=dict(color=[['#FFFFFF'] * (len(df_product) // 2)]),
        align='center',
        font=dict(size=12),
    )
)])
fig_product.update_layout(
    title="Total Quantity and Sales by Product Type",
    title_x=0.5,
    height=400,
    template="plotly_dark"
)

# Row 2 - Column 1: Hourly Total Sales (Line Chart)
curs.execute('''
SELECT
  SUBSTR(ORDER_TIMESTAMP, 1, 13) AS hour,
  SUM(TOTAL_PRICE) AS totalSales
FROM 5_join_group
GROUP BY hour
ORDER BY hour;
''')
tables = [row for row in curs.fetchall()]
hours = [f"{row[0][10:13]}:00" for row in tables]
total_sales = [row[1] for row in tables]

fig_hourly = go.Figure()
fig_hourly.add_trace(go.Scatter(
    x=hours,
    y=total_sales,
    mode='lines+markers',
    name='Total Sales',
    line=dict(color='blue'),
    marker=dict(size=8)
))
fig_hourly.update_layout(
    title='Hourly Total Sales',
    xaxis_title='Times',
    yaxis_title='Total Sales',
    height=500,
    width=900,
    template="plotly_dark"
)

# Row 2 - Column 2: Gender Distribution (Pie Chart)
curs.execute('''
SELECT
  gender,
  COUNT(*) AS userCount
FROM 2_users
GROUP BY gender
ORDER BY userCount DESC;
''')
tables = [row for row in curs.fetchall()]
genders = [row[0] for row in tables]
user_counts = [row[1] for row in tables]

fig_gender = go.Figure(go.Pie(
    labels=genders,
    values=user_counts,
    hole=0.3,
    textinfo='label+percent',
    marker=dict(colors=['#FF9999', '#66B3FF'])
))
fig_gender.update_layout(
    title='Gender Distribution of Users',
    height=500,
    width=500,
    template="plotly_dark"
)

# Layout: 2 Rows, 2 Columns with padding
col1_row1, col2_row1 = st.columns(2)
with col1_row1:
    st.plotly_chart(fig_country, use_container_width=True)
with col2_row1:
    st.plotly_chart(fig_product, use_container_width=True)

col1_row2, col2_row2 = st.columns(2)
with col1_row2:
    st.plotly_chart(fig_hourly, use_container_width=True)
with col2_row2:
    st.plotly_chart(fig_gender, use_container_width=True)
