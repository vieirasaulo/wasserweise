import sys 
sys.dont_write_bytecode = True #ignore __pycache__

import os
import pandas as pd
import numpy as np
from datetime import timedelta
import panel as pn
pn.extension('tabulator', sizing_mode="stretch_width")
import hvplot.pandas
import datetime
# import warnings
# warnings.filterwarnings('ignore')

path = 'D:\Repos\PirnaCaseStudy'
sys.path.append(path)
import SMARTControl as sc

import streamlit as st
from streamlit_folium import st_folium as stf

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

os.chdir(path)
database_fn = 'Data/Database.db' 
Get = sc.queries.Get(database_fn) # Instantiating the variable



#Querying the database

MonitoringPointData_df = Get.MonitoringPointData(GageData = 1) 
GageData_df = Get.GageData

# First and last date
start, end = Get.StartEndDate ()

#All variables 
Variables_df = Get.Table('Variables')

#Hydraulic heads
Get.LongTimeSeries(0)
df = Get.LongTimeSeries_df.copy()
df = df.set_index('Date')

#River data
Get.ShortTimeSeries(7, 'RG')
r_df = Get.ShortTimeSeries_df.copy()
r_df = r_df.set_index('Date')




st.sidebar.header('SMART`Control`')
st.sidebar.subheader('Parameters for the potentiometric map')
date_wid = st.sidebar.date_input(
    'Date',
    min_value = datetime.date(start.year,start.month,start.day),
    max_value = datetime.date(end.year,end.month,end.day),
    value = datetime.date(end.year,end.month,end.day)
                             )
# st.date_input(label, value=None, min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None, *, disabled=False, label_visibility="visible")

# time_wid = st.sidebar.date_input(
#     'Time',
#     min_value = 0),
#     max_value = datetime.date(end.year,end.month,end.day),
#                              )

st.sidebar.markdown('''
---
Created with ❤️ by [Saulo](https://github.com/SauloVSFh).
''')


#Dashboard

# col1 = st.columns(1)

# with col1:
st.markdown('### Potentiometric map of Pirna')

map_gdf, river_gage_gdf = sc.utils.prepare_query (Get, str(date_wid))


grid_x_gcs , grid_y_gcs , grid_z_gcs, U , V = sc.utils.Interpolation_Gradient (map_gdf , crs_utm = 25833 ,
                                                                                pixel_size = 10)

x = grid_x_gcs
y = grid_y_gcs

arrows_df = sc.utils.arrow_head (grid_x_gcs , grid_y_gcs , grid_z_gcs, U , V , scale = 10)
df = arrows_df [ arrows_df.index.isin( np.arange(0 ,
                                                  arrows_df.shape[0],
                                                  2
                                                )
                                      )
                ].reset_index (drop = True)

    
Map = sc.utils.Folium_map(Get)

Map_contour = sc.utils.Folium_contour (    
    Map , map_gdf , river_gage_gdf , 
    grid_x_gcs , grid_y_gcs , grid_z_gcs
                                      )

# arrows_df
Map = sc.utils.Folium_arrows(Map_contour , df )

stf(Map, height = 500 , width = 1400)