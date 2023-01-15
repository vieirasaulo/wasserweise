import os
import pandas as pd
import numpy as np
from datetime import timedelta
import panel as pn
pn.extension('tabulator', sizing_mode="stretch_width")
import hvplot.pandas

import warnings
warnings.filterwarnings('ignore')
import SMARTControl as sc
import streamlit as st
import hvplot.pandas
import holoviews as hv
import plost





@st.cache (allow_output_mutation=True)  # No need for TTL this time. It's static data :)
def Querying():
    database_fn = 'Data/Database.db' 
    Get = sc.queries.Get(database_fn) # Instantiating the variable
    
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
    
    g_df = df.groupby(['Name', pd.Grouper(freq='D')])['Value'].mean().to_frame().reset_index()
    g_df = g_df.rename (columns = {'Name' : 'MonitoringPointName'})

    gr_df = r_df.groupby(['MonitoringPointName', pd.Grouper(freq='D')])['Value'].mean().to_frame().reset_index()
    g_df_ = pd.concat ([g_df, gr_df])
    
    return Get, g_df, gr_df

Get, g_df, gr_df = Querying()



### Widgets

wells_wid = st.selectbox(
    'Choose well',
    list(g_df.MonitoringPointName.unique()))

def iTS ():

    g1_df = g_df [
        g_df.MonitoringPointName == wells_wid
    ].reset_index(drop = True)  
    
    maxy , miny = 115, 107
    
    # st.line_chart(
    #     g_df,  x = 'Date', y = 'Value',
    #     height = 500
    #     )
    
    iScatterTS = g1_df.hvplot.scatter(
        
        x = 'Date', y = 'Value',
        label = 'Diver Data',
        # frame_height = 500,
        alpha = 0.4,
        grid = True, 
        size = 50,
        ylabel = 'Hydraulic head (m)', 
        xlabel = 'Time',
        color = 'aqua',
        legend = True,
        # ylim= ( miny , maxy)
        
        )
    
    scatter_rg = gr_df.hvplot.scatter(
        
        x='Date', y='Value',
        ylabel = '[m]',
        xlabel = 'Date', 
        size = 50, 
        # frame_height = 500,
        # height = 500,
        color = 'green',
        label = "River Data",
        alpha = 0.4, 
        grid = True,
        clabel = 'River head',
        # ylim= ( miny , maxy)
        )
    
    iScatterTS =  scatter_rg * iScatterTS
    
    
    iScatterTS.opts(height = 600, width=1200, responsive=True)
    
    
    # col1, col2, col3 = st.columns((3,12,3))
    # with col1:
    #     st.write(' ')

    # with col2:
    st.write(hv.render(iScatterTS, backend='bokeh'))
    
    # with col3:
    #     st.write(' ')
    
    
    

iTS()

