import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the data
df = pd.read_csv('data/df_finale.csv')

# Convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Streamlit app title
st.title('COVID-19 Data Visualization')

# Sidebar for country selection
countries = df['Country/Region'].unique()
selected_country = st.sidebar.selectbox('Select a country', countries)

# Sidebar for graph type selection
graph_type = st.sidebar.selectbox('Select graph type', ['Line', 'Pie'])

# Filter data for the selected country
country_data = df[df['Country/Region'] == selected_country]

# Plotting
st.subheader(f'COVID-19 Trends in {selected_country}')
if graph_type == 'Line':
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(country_data['Date'], country_data['Deaths'], label='Deaths', color='red', linewidth=2)
    ax.plot(country_data['Date'], country_data['Recovered'], label='Recovered', color='green', linewidth=2)
    ax.plot(country_data['Date'], country_data['Active'], label='Active Cases', color='blue', linewidth=2)
    
    # Formatting axes
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Cases')
    ax.set_title(f'COVID-19 Trends in {selected_country}')
    ax.legend()
    
    # Format x-axis
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=30)
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Show the plot
    st.pyplot(fig)
elif graph_type == 'Pie':
    # Preparing data for pie chart
    latest_data = country_data.iloc[-1]
    labels = ['Deaths', 'Recovered', 'Active']
    sizes = [latest_data['Deaths'], latest_data['Recovered'], latest_data['Active']]
    colors = ['red', 'green', 'blue']
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title(f'COVID-19 Distribution in {selected_country} on {latest_data["Date"].date()}')
    
    # Show the plot
    st.pyplot(fig)
