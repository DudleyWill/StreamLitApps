import pandas as pd
import glob
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import os
import seaborn as sns
st.set_page_config(layout="wide")

# os.chdir(r'C:\Users\dudleyW\Downloads\DemandForecast\StreamLit')

list_file = [f for f in glob.glob('*.xlsx')]

# pd.set_option('precision', 0)
if 'file_name' not in st.session_state:
    st.session_state['file_name'] = 'new_data'

# here is how to create containers
@st.cache(ttl=60, max_entries=20, suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def ProcessData(file):
    column_names = ['VehicleType', 'Color', 'Manufacturer', 'Model', 'ModelYear', 'Fuel']
    df_gas = pd.read_excel(file, sheet_name='Gas', header=None, skiprows=1)
    df_diesel = pd.read_excel(file, sheet_name='Diesel', header=None, skiprows=1)
    df_gas.columns = column_names
    df_diesel.columns = column_names
    df_gas.dropna(subset=["ModelYear"], axis=0, inplace=True)
    df_diesel.dropna(subset=["ModelYear"], axis=0, inplace=True)
    # df_diesel['Model'] = df_diesel['Model'].astype(str)
    # df_gas['Model'] = df_gas['Model'].astype(str)
    # df_diesel['ModelYear'] = df_diesel['ModelYear'].astype(int)
    # df_gas['ModelYear'] = df_gas['ModelYear'].astype(int)
    gp_gas = df_gas.groupby(['ModelYear', 'Fuel'])['Model'].count().reset_index()
    gp_diesel = df_diesel.groupby(['ModelYear', 'Fuel'])['Model'].count().reset_index()
    df_car_by_year = pd.concat([gp_gas, gp_diesel], ignore_index=True)
    return df_car_by_year, df_gas, df_diesel

header_container = st.container()
data_container = st.container()
graph_container = st.container()

with st.sidebar:
    vehicle_option = st.radio(
        "Select Vehicle to investigate",
        ('Bus', 'Cars', 'Jeeps', 'MotorCycles', 'Pickups', 'SUVs', 'Trucks', 'Vans')
    )

    if vehicle_option == 'Bus':
        file = 'Bus.xlsx'
        graph_data, gas, diesel = ProcessData(file)
    elif vehicle_option == 'Cars':
        file = 'Cars.xlsx'
        graph_data, gas, diesel = ProcessData(file)
    elif vehicle_option == 'Jeeps':
        file = 'Jeeps.xlsx'
        graph_data, gas, diesel = ProcessData(file)
    elif vehicle_option == 'MotorCycles':
        file = 'MotorCycles.xlsx'
        graph_data, gas, diesel = ProcessData(file)
    elif vehicle_option == 'Pickups':
        file = 'Pickups.xlsx'
        graph_data, gas, diesel = ProcessData(file)
    elif vehicle_option == 'SUVs':
        file = 'SUVs.xlsx'
        graph_data, gas, diesel = ProcessData(file)
    elif vehicle_option == 'Trucks':
        file = 'Trucks.xlsx'
        graph_data, gas, diesel = ProcessData(file)
    else:
        file = 'Vans.xlsx'
        graph_data, gas, diesel = ProcessData(file)
    st.success('input file has been loaded')
    # data_load_state = st.text('Loading data...')
    # data_load_state.text("Done! (using st.cache)")
with header_container:
    st.title("My  first streamlit app for visualizing vehicle composition")
    st.header("Welcome!")
    # st.subheader("This is a great app")
    st.write("Please select a file from your computer to begin. You can use the list on the side to change vehicle "
             "type afterwards ")

with data_container:
    # read sheets and combine into one dataframe with gas and diesel per year
    st.subheader("Explore raw data by fuel type")

    figd = go.Figure(data=[go.Table(
        header=dict(values=list(['VehicleType', 'Color', 'Manufacturer', 'Model', 'ModelYear']),
                    fill_color='blue',
                    align='left'),
        cells=dict(values=[diesel.VehicleType, diesel.Color, diesel.Manufacturer, diesel.Model,diesel.ModelYear],
                   fill_color='black',
                   align='left'))
    ])
    figg = go.Figure(data=[go.Table(
        header=dict(values=list(['VehicleType', 'Color', 'Manufacturer', 'Model', 'ModelYear']),
                    fill_color='blue',
                    align='left'),
        cells=dict(values=[gas.VehicleType, gas.Color, gas.Manufacturer, gas.Model, gas.ModelYear],
                   fill_color='black',
                   align='left'))
    ])

    if st.checkbox('Click to view'):
        cola, colb = st.columns(2)
        with colb:
            fuel = st.radio(
                "Choose type of fuel to view data ",
                ('Diesel', 'Gas'))
        with cola:
            if fuel == 'Diesel':
                st.plotly_chart(figd)
            else:
                st.plotly_chart(figg)

with graph_container:
    st.subheader("Vehicle composition based on manufactured year")
    if st.checkbox('Click reveal'):
        fig = px.bar(graph_data, x='ModelYear', y='Model', color='Fuel',
                     labels={'ModelYear': '# of Vehicles', 'index': "manufactured year"}
                     )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Vehicle composition based on manufactured year")
    if st.checkbox('Click to reveal'):
        col1, col2= st.columns(2)
        with col2:
            values = st.slider('Select vehicle ranking range ', 0, 15, 3)
        with col1:
            fuel = st.radio(
                "Select fuel type ",
                ('Diesel', 'Gas'))
        if fuel == 'Diesel':
            df_pop = diesel['Model'].value_counts()[:values].reset_index()
            fig = px.bar(df_pop, y='Model', x='index', labels={'Model': '# of Vehicles', 'index': 'vehicle model'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            df_pop = gas['Model'].value_counts()[:values].reset_index()
            fig = px.bar(df_pop, y='Model', x='index', labels={'Model': '# of Vehicles', 'index': 'vehicle model'})
            st.plotly_chart(fig, use_container_width=True)
