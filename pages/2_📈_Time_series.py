import pandas as pd
import panel as pn
pn.extension('tabulator', sizing_mode="stretch_width")
import hvplot.pandas

import warnings
warnings.filterwarnings('ignore')
import SMARTControl as sc
import streamlit as st
import hvplot.pandas
import holoviews as hv
import warnings
warnings.filterwarnings('ignore')
import utils_dashboard as utl



def main():    
    # Settings
    utl.set_page_title('SMARTControl')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    # Loading CSS
    utl.local_css("frontend/css/streamlit.css")
    utl.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
    
    st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

main()


sc.utils.header()


@st.cache (allow_output_mutation=True)  # No need for TTL this time. It's static data :)
def Querying():
    database_fn = 'Data/Database.db' 
    Get = sc.queries.Get(database_fn) # Instantiating the variable
    
    # First and last date
    start, end = Get.StartEndDate ()

    
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
    
    return Get, g_df, gr_df

Get, g_df, gr_df = Querying()



### Sidebar

wells_wid = st.sidebar.selectbox(
    'Choose well',
    list(g_df.MonitoringPointName.unique()))


def iTS ():

    g1_df = g_df [
        g_df.MonitoringPointName == wells_wid
    ].reset_index(drop = True)  
    
    maxy , miny = 115, 107
    
    
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
    
    
    iScatterTS.opts( responsive=True)
    
    
    col1, col2, col3 = st.columns((8,12,8))
    with col1:
        st.write(' ')

    with col2:
        st.write(hv.render(iScatterTS, backend='bokeh'))
    
    with col3:
        st.write(' ')

iTS()

sc.utils.bottom()



