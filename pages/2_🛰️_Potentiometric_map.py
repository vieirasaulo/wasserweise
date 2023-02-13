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

@st.cache_resource
def Connect():
    database_fn = 'Data/Database.db' 
    Get = sc.queries.Get(database_fn) # Instantiating the variable
    return Get

Get = Connect()

@st.cache_data
def Querying():
    MonitoringPointData_df = Get.MonitoringPointData(GageData = 1) 
    GageData_df = Get.GageData
    
    # First and last date
    start, end = Get.StartEndDate ()
        
    return MonitoringPointData_df ,GageData_df, start, end


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


MonitoringPointData_df , GageData_df, start, end = Querying()


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
                        'Date and Time', 'Type of measurement', 'Head (m.a.s.l.)', 'E', 'N']
    
    
    wells = map_gdf.MonitoringPointName.unique()
    wells_option = list(wells)
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
    
    return print_df
    

def iTable (print_df):
    if st.button ('Traceback diver readings'):
        Get.Isolines_debug(
            Year = pd.to_datetime(date_wid).year,
            Month = pd.to_datetime(date_wid).month,
            Day = pd.to_datetime(date_wid).day,
            Hour = pd.to_datetime(date_wid).hour
            )
        
        debug_df = Get.Isolines_debug_df.copy().reset_index(drop = True)
        
        debug_df.columns = [
            'Monitoring Point ID', 'Monitoring Point Name', 'Case Top', 
            'Diver Depth', 'Diver Name', 'Date and Time', 'Type of measurement', 
            'Head (m.a.s.l.)', 'E', 'N', 'Diver Readings'
            ]
        
        st.dataframe(
            debug_df.style.format({
                'Case Top': '{:.2f}',
                'Head (m.a.s.l.)' : '{:.2f}',
                'Diver Readings': '{:.2f}',
                'Value': '{:.2f}',
                'Diver Depth': '{:.2f}',
                }),
            use_container_width=True
            )
             
        df = debug_df
    else:        
        st.dataframe(
            print_df.style.format({
                'Case Top' : '{:.2f}',
                'Head (m.a.s.l.)' : '{:.2f}',
                'Diver Readings' : '{:.2f}',
                'Value': '{:.2f}',
                'DiverDepth': '{:.2f}',
                }),
            use_container_width=True
        )
        df = print_df
    return df
             
print_df = iMap()
df = iTable(print_df)

#download button
dt = str(df['Date and Time'].unique()[0]).\
    replace(':','-').\
        split('.')[0]
        
file_name = f"HydraulicHeads_{dt}.csv"

csv = convert_df(df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name=file_name,
    mime='text/csv',
)

sc.utils.bottom()