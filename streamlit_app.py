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

# # Sidebar for date range selection
# start_date = st.sidebar.date_input('Start date', df['Date'].min())
# end_date = st.sidebar.date_input('End date', df['Date'].max())

# Sidebar for date range selection
start_date = st.sidebar.date_input('Start date', df['Date'].min())
end_date = st.sidebar.date_input('End date', df['Date'].max())


# Sidebar for data type selection
data_types = ['Deaths', 'Recovered', 'Active']
selected_data_types = st.sidebar.multiselect('Select data types', data_types, default=data_types)

# Sidebar for graph type selection
graph_type = st.sidebar.selectbox('Select graph type', ['Line', 'Pie'])

# Filter data for the selected country and date range
filtered_data = df[(df['Country/Region'] == selected_country) & (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

# # Plotting
# st.subheader(f'COVID-19 Trends in {selected_country}')
# if graph_type == 'Line':
#     fig, ax = plt.subplots(figsize=(10, 6))
#     for data_type in selected_data_types:
#         ax.plot(filtered_data['Date'], filtered_data[data_type], label=data_type, linewidth=2)
    
#     # Formatting axes
#     ax.set_xlabel('Date')
#     ax.set_ylabel('Number of Cases')
#     ax.set_title(f'COVID-19 Trends in {selected_country}')
#     ax.legend()
    
#     # Format x-axis
#     ax.xaxis.set_major_locator(mdates.AutoDateLocator())
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#     plt.xticks(rotation=30)
    
#     # Add grid for better readability
#     ax.grid(True, linestyle='--', alpha=0.5)
    
#     # Show the plot
#     st.pyplot(fig)
# elif graph_type == 'Pie':
#     # Preparing data for pie chart
#     latest_data = filtered_data.iloc[-1]
#     sizes = [latest_data[data_type] for data_type in selected_data_types]
#     colors = ['red', 'green', 'blue']
    
#     fig, ax = plt.subplots(figsize=(8, 8))
#     ax.pie(sizes, labels=selected_data_types, colors=colors[:len(selected_data_types)], autopct='%1.1f%%', startangle=90)
#     ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
#     ax.set_title(f'COVID-19 Distribution in {selected_country} on {latest_data["Date"].date()}')
    
#     # Show the plot
#     st.pyplot(fig)


# Plotting
st.subheader(f'COVID-19 Trends in {selected_country}')
if graph_type == 'Line':
    fig, ax = plt.subplots(figsize=(10, 6))
    for data_type in selected_data_types:
        ax.plot(filtered_data['Date'], filtered_data[data_type], label=data_type, linewidth=2)
    
    # Formatting axes
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Cases')
    ax.set_title(f'COVID-19 Trends in {selected_country}')
    ax.legend()
    
    # Format x-axis to show dates
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=30)
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Show the plot
    st.pyplot(fig)
