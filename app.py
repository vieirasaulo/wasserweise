import os
import sys
import time
from datetime import timedelta, datetime
import folium
import numpy as np
import pandas as pd

import folium

import panel as pn
pn.extension('tabulator', sizing_mode='stretch_width')

import holoviews as hv
import hvplot.pandas
hv.extension('bokeh')

#Fetching Repo capabilities
path = 'd:/repos/pirnacasestudy'
sys.path.append('d:/repos/pirnacasestudy')
import SmartControl as sc

#instantiating class to query the database
os.chdir(path)
Get = sc.queries.Get('Data/database.db')


MonitoringPointData_df = Get.MonitoringPointData(GageData = 1)
GageData_df = Get.GageData

'''
Querying the database
'''

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

# Check if HydroPlot goes and add it here


'''

Widgets

'''
wells_list = list(df.Name.unique())
wells_wid = pn.widgets.Select (name = 'Well', options = wells_list, value = wells_list[0])



wells_df = MonitoringPointData_df.copy()
wells_df = wells_df.iloc[:,1:] [ wells_df['Type'] == 'Well']
# wells_df['Lon'], wells_df ['Lat'] = hv.util.transform.lon_lat_to_easting_northing(wells_df.E, wells_df.N)    




# var_wid = pn.widgets.Select(name='Variable', options = list(Variables_df.Description))

value = end - timedelta(days=2) 
date_wid = pn.widgets.DatetimePicker(name='Date and time', start=start , end = end, value = value)
scalearrows_wid = pn.widgets.IntSlider(start = 10, end = 500 , step = 20, value = 250,
                                      name='Sizing arrows'
                                      )


'''

Time Series

'''                                      
PALETTE = ["#00CED1", "#006400"]

    
g_df = df.groupby(['Name', pd.Grouper(freq='D')])['Value'].mean().to_frame().reset_index()
gr_df = r_df.groupby(['Name', pd.Grouper(freq='D')])['Value'].mean().to_frame().reset_index()
g_df = pd.concat ([g_df, gr_df])



def iTS (wells_wid):

    g1_df = g_df [
        g_df.Name == wells_wid
    ].reset_index(drop = True)  
    
    
    return g1_df

iBindTS = hvplot.bind(iTS, wells_wid).interactive()


iScatterTS = iBindTS.hvplot.scatter(
    x = 'Date', y = 'Value',
    label = 'Diver Data',
    width = 1400, alpha = 0.4, grid = True, size = 50,
    ylabel = 'Hydraulic head (m)', xlabel = 'Time',
    color = 'aqua', legend = True,
                           )

scatter_rg = gr_df.hvplot.scatter(
    x='Date', y='Value',
    ylabel = '[m]',
    xlabel = 'Date', 
    size = 50, 
    width = 1400,
    height =500,
    color = 'green',
    label = "River Data",
    alpha = 0.4, grid = True,
    clabel = 'River head'
                                )

iScatterTS =  scatter_rg *iScatterTS

'''

MAP

'''


text=  pn.pane.Markdown ('''
        # <center>Not enough data on this date</center>
        <br>
        ''',align = 'center', style = {'font-size' : '1.5em'})


def iPlot (date_wid, scalearrows_wid):
    
    try :
    
        map_gdf, river_gage_gdf = sc.utils.prepare_query (Get, date_wid )



        grid_x_gcs , grid_y_gcs , grid_z_gcs, U , V = sc.utils.Interpolation_Gradient (map_gdf , crs_utm = 25833 ,
                                                                                       pixel_size = 10)

        x = grid_x_gcs
        y = grid_y_gcs

        arrows_df = sc.utils.arrow_head (grid_x_gcs , grid_y_gcs , grid_z_gcs, U , V , scale = scalearrows_wid)
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

        return pn.pane.plot.Folium(Map, height = 690,
                                   
                                  )
    
    except Exception:
        
        return text

iMap = pn.bind(iPlot, date_wid, scalearrows_wid)




'''
Dashboard

app

'''




Row1 = pn.Row(date_wid , scalearrows_wid)
Row2 = pn.Row(iMap)
iMap_col = pn.Column(Row1, Row2,
                    height_policy = 'fit',
                    sizing_mode = 'stretch_width',
                    )
                    
 # Header
Inowas_fn = 'Figures/INOWAS.jpg'
SMARTControl_fn = 'Figures/SmartControl.png'
dashboard_title = pn.panel('## SMART-Control')
col1_r1 = pn.Column(pn.pane.JPG(Inowas_fn, height=40))
col2_r1 = pn.Column(pn.pane.PNG('Figures/SmartControl.png', height=40))


row1 = pn.Row(col1_r1, pn.Spacer(width=450),
              col2_r1,  background='aqua',
              height = 50, height_policy = 'fixed',
              sizing_mode = 'stretch_width',
             ) #top, right, bottom, left in pxls col3_r1, margin=(0, 100, 0, -5),

#Tabs
row2 = pn.Tabs (('Map', iMap_col) ,
                ('Scatter', iScatterTS), 
                sizing_mode = 'stretch_both'
               )


#Bottom
Groundwatch_fn = 'Figures/Groundwatch.png'
Python_fn = 'Figures/Python-logo-notext.png'
PegelAlarm_fn = 'Figures/INOWAS.jpg'
TUDresden_fn = 'Figures/TuDresden.png'

col1_r3 = pn.Column(pn.pane.PNG(Groundwatch_fn, height=40))
col2_r3 = pn.Column(pn.pane.PNG(Python_fn, height=40))
col3_r3 = pn.Column(pn.pane.PNG('Figures/PegelAlarm.png', height=40))
col4_r3 = pn.Column(pn.pane.PNG(TUDresden_fn, height=40))


row3 = pn.Row(
    col1_r3, col2_r3 , col3_r3, col4_r3, 
    background='turquoise',
    height = 50, height_policy = 'fixed',
    sizing_mode = 'stretch_width' 
             )




dashboard = pn.Column(row1 ,row2, row3)

dashboard.servable()                  
dashboard.serve()                  
