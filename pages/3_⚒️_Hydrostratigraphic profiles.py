import streamlit as st

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
    
    Get.HydroProfile()
    HydroProfile_df = Get.HydroProfile_df.copy()
    HydroProfile_df.columns = [
        'ID', 'PointID', 'DrillName', 'TestType', 'Unit', 'Depth', 'DrillDepth','MonitoringPoint', 'Value', 'E', 'N'
    ]

    
    layers_df = pd.DataFrame({
        "Drill"   : [
            'D-G01', 'D-G02', 'D-G03', 'D-G05', 'D-G10', 'D-G11', 
            'D-G12', 'D-G13', 'D-G15','D-G17', 'D-G19', 'D-G21'
        ],
        "Landfill": [-3.0, -3.0 ,-3.0 ,-3.0 ,-3.0 , 0.0,  0.0,  0.0 , 0.0,  0.0,  0.0,  0.0],
        "Layer 1": [-3.7, -3.7,- 3.8, -4.0, -2.9, -4.0, -4.3, -3.5, -4.0, -4.2, -4.0, -3.9],
        "Layer 2": [-2.2, -3.1, -3.2, -3.3, -4.8, -4.0, -3.0, -3.8, -3.7, -3.3, -3.1, -2.9],
        "Layer 3": [-3.1, -3.2, -2.9, -2.9, -2.2, -4.1, -4.6, -4.8, -4.5, -4.0, -4.7, -3.4],
        "Layer 4": [-2.0, -1.0, -1.1, -0.8, -1.1, -1.9, -2.1, -1.9, -1.8, -2.5, -2.2, -0.0]})
        
    #handling log
    HydroProfile_df.Depth *= -1
    HydroProfile_df.Value = np.where(HydroProfile_df.Value < 0, 0, HydroProfile_df.Value)
    # HydroProfile_df.Value  = np.log10 (HydroProfile_df.Value)    

    plot_df = HydroProfile_df [
        (HydroProfile_df.TestType.isin (['EC logs', 'DPIL']))
    ].reset_index(drop = True)  

    
    return Get, plot_df, layers_df

Get, HydroProfile_df, layers_df = Querying()

drills_wid = st.selectbox(
    'Choose drill',
    list(HydroProfile_df.DrillName.unique()))


######################### Plots

height = 500


def iHPV():
    df =  HydroProfile_df [
        (HydroProfile_df.DrillName == drills_wid)
    ].reset_index(drop = True)  
        
    
    message = '''
    ### <center>No data for this drill</center>
    '''
    
    
    if df.shape[0] == 0:
        st.markdown (message)
        
    else:
        df = df.replace(['EC logs', 'DPIL'], ['EC [mS/m]', 'Kr-DPIL[l/h*bar]'])
        df = df.rename (columns = {"TestType" : "Variable"})
        
        iLineHP = df.hvplot.line(
            x = 'Value',
            y = 'Depth',
            by = 'Variable',
            alpha = 1,
            logx = True,
            grid = True,
            ylabel = 'Depth (m)', 
            xlabel = 'Log',
            legend = True,
            ylim = [df.Depth.min() - 2,1],
            height = height,
            width = 600
    )

        st.write(hv.render(iLineHP, backend='bokeh')) 
        
        
    df_ = layers_df [
        (layers_df.Drill== drills_wid)
    ].reset_index(drop = True)  

    #dropping columns that contain zero - getting rid of the layers that do not have landfills
    df_ = df_.loc [:,(df_ != 0).any(axis=0) ]
    
    if df_.shape[0] == 0:
        st.markdown (message)
    
    else:
        iBarHP = df_.hvplot.bar(
            x        = 'Drill',
            stacked  = True,
            xlim = [0,4],
            ylim = [df.Depth.min() - 2,1],
            color    = ['#ED7D31', '#FFC000', '#70AD47', '#9E480E', '#997300'],
            height   = height,
            width = 200,
            xlabel = ''
        )
    
        
        # iplot = (iLineHP + iBarHP)
        st.write(hv.render(iBarHP, backend='bokeh'))
        


iHPV()