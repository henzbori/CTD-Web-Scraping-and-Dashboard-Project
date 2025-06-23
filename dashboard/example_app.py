import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.data as data

df = data.gapminder()

st.title("Global GDP Dashboard")
st.markdown("GDP per Capita Over Time for selected country. Use dropdown to choose the country.")

st.subheader("Dataset display")
st.dataframe(df.head())

st.subheader("key statistics")
st.write(df.describe())

st.subheader("Data Cleaning Summary")
st.markdown("""
- Loaded `gapminder` dataset from Plotly
- Converted year to integer if needed
- Filtered data by selected country
""")

countries = df['country'].unique()
country = st.selectbox("Select a country:", sorted(countries), index=list(countries).index("Canada"))

filtered_df = df[df['country'] == country]

st.subheader(f"GDP per Capita Over Time for {country}")
fig = px.line(filtered_df, x='year', y='gdpPercap', title=f"{country}: GDP per Capita Growth")
st.plotly_chart(fig)

st.subheader(f"Life Expectancy Over Time for {country}")
fig2 = px.line(filtered_df, x='year', y='lifeExp', title=f"{country}: Life Expectancy")
st.plotly_chart(fig2)