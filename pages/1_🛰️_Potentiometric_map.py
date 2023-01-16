import sys 
sys.dont_write_bytecode = True #ignore __pycache__
import pandas as pd
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import datetime
import SMARTControl as sc
import streamlit as st
from streamlit_folium import st_folium as stf
import warnings
warnings.filterwarnings('ignore')
import utils_dashboard as utl



def main(fn):    
    # Settings
    utl.set_page_title('SMARTControl')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    # Loading CSS
    utl.local_css(fn)
    utl.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

main("frontend/css/streamlit.css")

sc.utils.header()

@st.cache (allow_output_mutation=True)  # No need for TTL this time. It's static data :)
def Querying():
    database_fn = 'Data/Database.db' 
    Get = sc.queries.Get(database_fn) # Instantiating the variable
    
    MonitoringPointData_df = Get.MonitoringPointData(GageData = 1) 
    GageData_df = Get.GageData
    
    # First and last date
    start, end = Get.StartEndDate ()
    
    return Get, MonitoringPointData_df ,GageData_df, start, end

Get, MonitoringPointData_df ,GageData_df, start, end = Querying()


#### Sidebar widgets

scale_wid = st.sidebar.slider('Size of arrows', min_value=1, max_value=100, value=10, step=1)

date_wid = st.sidebar.date_input(
    'Date',
    min_value = datetime.date(start.year,start.month,start.day),
    max_value = datetime.date(end.year,end.month,end.day),
    value = datetime.date(end.year,end.month,end.day)
                              )

hour_wid = st.sidebar.slider('Hour', min_value=0, max_value=24, value=0, step=1)



def iMap ():
    
    st.markdown(
        "<h3 style='text-align: center; color: black;'>Potentiometric map of Pirna test field</h3>",
                unsafe_allow_html=True)
       

    
    date_wid_ = date_wid + pd.DateOffset(hours= hour_wid)
    
    map_gdf, river_gage_gdf = sc.utils.prepare_query (Get, date_wid_)

    
    print_df = map_gdf [[col for col in map_gdf.columns if col != 'geometry']]
    print_df = pd.DataFrame(print_df)
    
    print_df = print_df.drop_duplicates('MonitoringPointName')
    
    print_df.columns = ['Monitoring Point ID', 'Monitoring Point Name', 
                        'Date and Time', 'Type of measurement', 'Value (m.a.s.l.)', 'E', 'N']
    
    
    wells = map_gdf.MonitoringPointName.unique()
    wells_option = [well for well in wells if 'W' not in well]
    
    wells_wid = st.sidebar.multiselect(
        'Choose wells',
        wells,
        wells_option)
    
    map_gdf = map_gdf [map_gdf.MonitoringPointName.isin(wells_wid)].reset_index(drop=True)
    
    
    grid_x_gcs , grid_y_gcs , grid_z_gcs, U , V = sc.utils.Interpolation_Gradient (map_gdf , crs_utm = 25833 ,
                                                                                    pixel_size = 10)
    
    arrows_df = sc.utils.arrow_head (grid_x_gcs , grid_y_gcs , grid_z_gcs, U , V , scale = scale_wid)
    arrows_df = arrows_df [ 
        arrows_df.index.isin( np.arange(0 , arrows_df.shape[0], 2))
                    ].reset_index (drop = True)
    
    Map = sc.utils.Folium_map(Get)
    
    Map_contour = sc.utils.Folium_contour (    
        Map , map_gdf , river_gage_gdf , 
        grid_x_gcs , grid_y_gcs , grid_z_gcs
                                          )
    
    # arrows_df
    m = sc.utils.Folium_arrows(Map_contour , arrows_df )
    
    stf(m, height = 600 , width = 1800)
    
    

    
    col1, col2, col3 = st.columns((4,12,4))
    
    
    with col1:
        st.write(' ')

    with col2:
        st.write(print_df, width = 1500)
    
    with col3:
        st.write(' ')
             
iMap()
sc.utils.bottom()