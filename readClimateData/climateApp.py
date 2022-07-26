
import pandas as pd
import glob
import streamlit as st
from functools import reduce
import glob
import linecache
import os
import plotly.express as px
import geopandas as gpd
from shapely.geometry import Point
from functools import reduce
from shapely import speedups
speedups.enabled
import plotly.graph_objects as go
import os
st.set_page_config(layout="wide")


header_container = st.container()
csgm_container = st.container()
ckk_container = st.container()

@st.cache(ttl=60, max_entries=20, suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def ProcessData(file,parish):
    # fLine = linecache.getline(file, 3)
    # parish = fLine.rsplit(',', 2)[1][:-1]

    df_all = pd.read_csv(file , header=None, skiprows=4,low_memory=True,sep=",", error_bad_lines=False )
    df_all.columns = ['year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    #
    df_melted = pd.melt(df_all, id_vars=['year'], var_name='month', value_name=parish + '_C')
    df_melted['date'] = pd.to_datetime(df_melted['year'].astype(str) + '-' + df_melted['month'] + '-01')
    df_melted.sort_values('date', inplace=True)
    df_melted.set_index('date', inplace=True)
    df_melted.drop(columns=['year', 'month'], inplace=True)
    # data_frames.append(melted)
    return df_melted, df_all

def chose_unit(x):
    if x.rsplit('_', 1)[1] == 'hurs':
        return '_RH'
    else:
        return '_K'

@st.cache(ttl=60, max_entries=20, suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def CSGMData(shp):
    country_shp = gpd.read_file(shp)
    return country_shp



@st.cache
def convert_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def convert_xlsx(df, fname):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_excel(fname + '.xlsx')


with header_container:
     st.header('Processes climate data for demand Forecasting ')

with st.sidebar:
    st.header('Choose File Controls')

    with st.expander("TXT Data file from CSGM"):
        weatherType1 = st.selectbox(
            'Select Weather variable being processed?',
            ('Humidity', 'Temperature', 'Rainfall', 'wind speed'))
        # st.write('You selected:', weatherType1)

        modelOption1 = st.radio(
            'Select model type',
            ('Non-HadGem', 'Hadgem'))
        if modelOption1 == "Non-HadGem":
            st.write('Non-HadGem')
        else:
            st.write('Hadgem')

        uploaded_file = st.file_uploader("select a txt from CSGM") # accept_multiple_files=True)
        if uploaded_file is not None:
            # Can be used wherever a "file-like" object is accepted:
            dataframe = pd.read_csv(uploaded_file)


        shp_file = st.file_uploader("select shapefile for country")  # accept_multiple_files=True)
        if uploaded_file is not None:
            # Can be used wherever a "file-like" object is accepted:
            country_shp = gpd.read_file(shp_file)


    with st.expander("CSV file from World Bank "):
        parish_name = st.text_input('Enter name of parish', 'BelizeCity')
        ckk_file = st.file_uploader("Select a csv file from the world bank")
        if not ckk_file:
            st.stop()

        if ckk_file is not None:
            # Can be used wherever a "file-like" object is accepted:
            ckk_data, raw_data = ProcessData(ckk_file, parish_name)


with csgm_container:
    with st.expander('Processed CSGM data '):
        st.write(dataframe)




with ckk_container:
    with st.expander('Processed data from the World Bank '):
        vis_choice = st.radio('choose data exploration options ',
                              ('Raw Data', 'Transformed Data', 'Graph'), horizontal=True)

        if vis_choice == 'Raw Data':
            st.dataframe(raw_data)
        elif vis_choice == 'Transformed Data':
            st.dataframe(ckk_data)
            dcol, dcol1 = st.columns([1,2])
            with dcol:
                download_name = st.text_input(' Enter file name, do not include extension ')
            with dcol1:
                st.text('')
                st.text('')

                csv = convert_csv(ckk_data)
                st.download_button(
                    label="Download data as csv ",
                    data=csv,
                    file_name=download_name + '.csv',
                    mime='text/csv',)


        else:
            # ckk_data = ProcessData(ckk_file)
            y_value = parish_name + '_C'
            yr_agg = st.slider("Use slider to change the number of months to calculate rolling mean ", 1, 120, 12)
            yr_val = str(yr_agg) + 'M'
            ckk_data_yr = ckk_data.resample(yr_val).mean()
            fig = px.line(ckk_data_yr, x=ckk_data_yr.index, y=y_value, title='Temperature data for ' + parish_name)
            st.plotly_chart(fig, use_container_width=True)
            # add metrics
            metric_data = ckk_data
            metric_data['year'] = metric_data.index.year

            # max_delta = round(t_max[0] - max_base[0], 1)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                filter_year = st.text_input("Change year to compare to lastest data ", value=1901, max_chars=4)
                first_yr_min = metric_data.loc[metric_data.year == int(filter_year)].min()[0]
                first_yr_max = metric_data.loc[metric_data.year == int(filter_year)].max()[0]
                # last year in data
                final_yr = metric_data.year[-1]
                last_yr_min = metric_data.loc[metric_data.year == final_yr].min()[0]
                last_yr_max = metric_data.loc[metric_data.year == final_yr].max()[0]
                # change between last and first year
                min_delta = round(last_yr_min - first_yr_min, 2)
                max_delta = round(last_yr_max - first_yr_max, 2)
                # min_base = metric_data.loc[metric_data.year == 1901].min()[0]
                t_min = ckk_data_yr.min().values
                t_max = ckk_data_yr.max().values

            col2.metric(label= filter_year +" min compared to " + str(final_yr), value=str(round(first_yr_min, 2)) + "°C", delta=str(min_delta) + "°C")
            col3.metric(label= filter_year + " max compared to " + str(final_yr), value=str(round(first_yr_max, 2)) + "°C", delta=str(max_delta) + "°C")

            with col4:
                filter_mean_yr = metric_data.loc[metric_data.year == int(filter_year)].mean()[0]
                last_mean_yr = metric_data.loc[metric_data.year == final_yr].mean()[0]
                avg_change = round(last_mean_yr - filter_mean_yr,2)
                st.metric(label= filter_year + " mean compared to " + filter_year, value=str(round(filter_mean_yr,2)) + "°C", delta=str(avg_change) + "°C")




