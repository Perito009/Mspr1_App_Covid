import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('df_finale.csv')

# Streamlit app title
st.title('COVID-19 Data Visualization')

# Sidebar for country selection
countries = df['Country/Region'].unique()
selected_country = st.sidebar.selectbox('Select a country', countries)

# Filter data for the selected country
country_data = df[df['Country/Region'] == selected_country]

# Plotting
st.subheader(f'COVID-19 Trends in {selected_country}')
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(country_data['Date'], country_data['Deaths'], label='Deaths', color='red')
ax.plot(country_data['Date'], country_data['Recovered'], label='Recovered', color='green')
ax.plot(country_data['Date'], country_data['Active'], label='Active Cases', color='blue')
ax.set_xlabel('Date')
ax.set_ylabel('Number of Cases')
ax.set_title(f'COVID-19 Trends in {selected_country}')
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)
