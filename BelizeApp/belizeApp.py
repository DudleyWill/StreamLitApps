import pandas as pd
import glob
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import os
import seaborn as sns
st.set_page_config(layout="wide")
import geopandas as gpd
from shapely.geometry import Point
from functools import reduce
from shapely import speedups
speedups.enabled



# read in shape file for the country
pathForModel = r'C:\Users\dudleyW\Downloads\Read_Weather_data\python_scripts\Guyana'
mapShape = r'C:\Users\dudleyW\Downloads\Read_Weather_data\python_scripts\Belize_Basemap\Belize_Basemap.shp'
belizeShp = gpd.read_file(mapShape)
belizeShp = belizeShp.to_crs(4326)
# if the district is broken up into several polygon. this merges into one large polygon
district = belizeShp.dissolve(by='DISTRICT', as_index=False)
district.reset_index(drop=True, inplace=True)
# this plots the shape file
ax = district.plot(cmap='plasma')
district.apply(lambda x: ax.annotate(text=x['DISTRICT'], xy=x.geometry.centroid.coords[0], ha='center'), axis=1)
plt.title('Coordinates of each parish for Belize')

# read in weather data
os.chdir(r'C:\Users\dudleyW\OneDrive - CCREEE\Documents\Outreach')
file = 'GFDL-ESM2M_rcp85_tasmax'
df_sub = pd.read_table(file + '.txt', sep='\s+', header=None, parse_dates=[[0, 1, 2]], nrows=150)
df_sub.columns = ["date", "lat", "long", "data"]
# plot graph of temperature coordinates
longlat = gpd.GeoSeries([Point(xy) for xy in zip(df_sub["long"], df_sub["lat"])])
fig, ax = plt.subplots(figsize=(7, 7))
longlat.plot(ax=ax, facecolor='red', edgecolor='k', alpha=1, linewidth=1)
plt.title('Temperature value coordinates ')

# this creates the overlay of the data
fig, ax = plt.subplots(figsize=(7, 7))
district.plot(ax=ax, facecolor='Grey', edgecolor='k', alpha=1, linewidth=1, cmap="plasma")
longlat.plot(ax=ax, facecolor='red', edgecolor='k', alpha=1, linewidth=1)
district.apply(lambda x: ax.annotate(text=x['DISTRICT'], xy=x.geometry.centroid.coords[0], ha='center'), axis=1)
plt.title('Overlay Coordinates of temperature and Parishes of Belize')

#

# this creates the overlay of the data
parish = district.loc[district['DISTRICT'] == 'Corozal']  # this parish
parish.reset_index(drop=True, inplace=True)
points_overlap = longlat.within(parish.at[0, 'geometry'])
coord = df_sub.loc[points_overlap]
intesectionCoord = gpd.GeoSeries([Point(xy) for xy in zip(coord["long"], coord["lat"])])
print(intesectionCoord)
#

fig, ax = plt.subplots(figsize=(7, 7))
parish.plot(ax=ax, facecolor='Grey', edgecolor='k', alpha=1, linewidth=1, cmap="plasma")
intesectionCoord.plot(ax=ax, facecolor='red', edgecolor='k', alpha=1, linewidth=1)
parish.apply(lambda x: ax.annotate(text=x['DISTRICT'], xy=x.geometry.centroid.coords[0], ha='center'), axis=1)
plt.title('Coordinates that intersect a parish')


# get points for individual parishes

df_all = pd.read_table(file + '.txt', sep='\s+', header=None, parse_dates=[[0, 1, 2]])
df_sub = pd.read_table(file + '.txt', sep='\s+', header=None, parse_dates=[[0, 1, 2]], nrows=150)
df_all.columns = ["date", "lat", "long", "data"]
df_sub.columns = ["date", "lat", "long", "data"]

# prepares the data to be filtered by parish to a list of dataframes
longlat = gpd.GeoSeries([Point(xy) for xy in zip(df_sub["long"], df_sub["lat"])])
area = ['Belize', 'Cayo', 'Corozal', 'Orange Walk', 'Stann Creek', 'Toledo']
data_frames = []
for i in area:
    district1 = district.loc[district['DISTRICT'] == i]  # this parish
    district1.reset_index(drop=True, inplace=True)
    points_overlap = longlat.within(district1.at[0, 'geometry'])
    cord = df_sub.loc[points_overlap]
    cordOfInterest = cord['long'].unique()
    df2 = df_all[df_all['long'].isin(cordOfInterest)]
    df2 = df2.groupby(["date"])['data'].mean()
    data = df2.reset_index()
    data.columns = ["date", i + '_K']
    data[i] = data[i + '_K'] - 273
    data = data.drop(i + '_K', axis=1)
    data.set_index('date', inplace=True)
    data_frames.append(data)
# produces a total file
df_merged = reduce(lambda left, right: pd.merge(left, right, on=['date'], how='outer'), data_frames)


# plot several graphs
def plotgraphMax(x):
    df_annual = df_merged.resample('A').max()
    year1 = str(x) + '-12-31'
    df_year = df_annual.loc[df_annual.index == year1]
    # This converts the column headings into row values, basically transpose the dataframe
    df_2028transpose = df_year.melt(var_name='ADM1', value_name='Temperature')
    # merge data column into the geodataframe
    fulldata1 = district.merge(df_2028transpose, left_on=['DISTRICT'], right_on=['ADM1'])
    ax1 = fulldata1.plot(column='Temperature', cmap='Dark2', legend=True)
    fulldata1.apply(lambda x: ax1.annotate(text=x['DISTRICT'], xy=x.geometry.centroid.coords[0], ha='center'), axis=1)
    plt.title('Color each Parish by Temperature_' + year1[:4])


def plotgraphAvg(x):
    df_annual = df_merged.resample('A').mean()
    year1 = str(x) + '-12-31'
    df_year = df_annual.loc[df_annual.index == year1]
    # this converts the column headings into row values, basically transpose the dataframe
    df_2028transpose = df_year.melt(var_name='ADM1', value_name='Temperature')
    # merge data column into the geodataframe
    fulldata1 = district.merge(df_2028transpose, left_on=['DISTRICT'], right_on=['ADM1'])
    ax1 = fulldata1.plot(column='Temperature', cmap='Dark2', legend=True)
    fulldata1.apply(lambda x: ax1.annotate(text=x['DISTRICT'], xy=x.geometry.centroid.coords[0], ha='center'), axis=1)
    plt.title('Color each Parish by Temperature_' + year1[:4])


