import pandas as pd
import panel as pn
pn.extension('tabulator', sizing_mode="stretch_width")
import warnings
warnings.filterwarnings('ignore')
import SMARTControl as sc
import streamlit as st
import warnings
warnings.filterwarnings('ignore')
import utils_dashboard as utl

# import plotly.graph_objects as go
import plotly.express as px



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


def iTS_ ():

    g1_df = g_df [
        g_df.MonitoringPointName == wells_wid
    ].reset_index(drop = True)  
    
    g1_df_ = pd.concat([g1_df,gr_df])
    
    fig = px.scatter(
        g1_df_,
        x='Date', y='Value',
        color = 'MonitoringPointName',
        height = 600,
        width = 1300,
        color_discrete_sequence = ['#01b2ff','green'],
        opacity = 0.5,
        
        )
    

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
    

    
    st.plotly_chart(fig)
    


iTS_()
sc.utils.bottom()



