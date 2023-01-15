import sys 
sys.dont_write_bytecode = True #ignore __pycache__

import os
import pandas as pd
import numpy as np
np.seterr(divide='ignore', invalid='ignore')

# import hvplot.pandas
import datetime
import SMARTControl as sc
import streamlit as st
from streamlit_folium import st_folium as stf
from PIL import Image
from pathlib import Path
import base64

from pathlib import Path
import streamlit as st

st.set_page_config(layout='wide', 
                   page_icon = "📡",
                   initial_sidebar_state='expanded')


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

markdown_fn = 'README.md'
intro_markdown = read_markdown_file(markdown_fn)
st.markdown(intro_markdown, unsafe_allow_html=True)


# @st.cache (allow_output_mutation=True)
Inowas_fn = 'Assets/INOWASV1.png'
SMARTControl_fn = 'Assets/SmartControl.png'
Groundwatch_fn = 'Assets/Groundwatchv1.png'
Python_fn = 'Assets/Python-logo-notext.png'
PegelAlarm_fn = 'Assets/PegelAlarm.png'
TUDresden_fn = 'Assets/TuDresden.png'



st.sidebar.header('SMART`Control`')
st.sidebar.success('Select a page above.')
st.sidebar.subheader('Parameters for the potentiometric map')






st.sidebar.markdown('''
---
Created with ❤️ by [Saulo, Nicolás and Cláudia](https://github.com/SauloVSFh/PirnaStudyCase)
''')



################# Cache

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
    
    return Get, MonitoringPointData_df ,GageData_df, start, end, Variables_df, df , r_df

@st.cache (allow_output_mutation=True)
def MapTile():
    Map = sc.utils.Folium_map(Get)
    return Map

Get, MonitoringPointData_df, GageData_df , start, end, Variables_df, df , r_df = Querying()



if "my_input" not in st.session_state:
    st.session_state["my_input"] = ""