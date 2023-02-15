import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import SMARTControl as sc
import streamlit as st
import warnings
warnings.filterwarnings('ignore')
import utils_dashboard as utl
import plotly.express as px
from plotly.subplots import make_subplots


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
database_fn = 'Data/Database.db' 
Get = sc.queries.Get(database_fn) # Instantiating the variable

@st.cache_data(ttl=3600)
def Querying:
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
    
    return g_df, gr_df

g_df, gr_df = Querying()

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


### Sidebar Widgets
wells_wid = st.sidebar.multiselect(
    'Choose wells', 
    options = list(g_df.MonitoringPointName.unique()),
    default = None,
    )


def iTS_ ():
    
    fig = make_subplots(rows=1, cols=1)
    
    #plot river gage data
    line_plot = px.line(
        gr_df,
        x='Date', y='Value',
        color = 'MonitoringPointName',
        color_discrete_sequence = ['green']
        )
    
    fig.add_trace(line_plot['data'][0], row=1, col=1)
    

    g1_df = g_df [
        g_df.MonitoringPointName.isin (wells_wid)
    ].reset_index(drop = True)  

    
    #plot wells
    scatter_plot = px.scatter(
        g1_df,
        x='Date', y='Value',
        color = 'MonitoringPointName',
        height = 600,
        width = 1300,
        color_discrete_sequence = px.colors.qualitative.Dark24,
        opacity = 0.5,
        )
    
    for elm in scatter_plot['data']:
        fig.add_trace(elm, row=1, col=1)
    

    fig.update_layout(
    font_color = '#7D7D7D', 
    xaxis_title="<b>Time<b>",
    yaxis_title="<b>[M.A.S.L.]</b>",
    legend_title="<b>Monitoring point</b>",
    yaxis=dict(color="black"),
    )

    
    fig.update_yaxes( 
        title_font_size = 20,
        tickfont_family = 'Times New Roman'
        )
    
    fig.update_xaxes( 
        color="black",
        tickfont_family = 'Times New Roman',
        )
    

    
    st.plotly_chart(fig, use_container_width=True)
    
    # df = pd.concat([g1_df, gr_df])
    # df.columns = ['Monitoring Point Name', 'Date and Time', 'Head (m.a.s.l.)']
    
    # return df

# df = 
iTS_()

# #download button
        
# file_name = "TimeSeries_HydraulicHeads.csv"

# csv = convert_df(df)

# st.download_button(
#     label="Download data as CSV",
#     data=csv,
#     file_name=file_name,
#     mime='text/csv',
# )

sc.utils.bottom()



