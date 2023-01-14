import sys 

'''
ignore __pycache__
add path to repo
'''
sys.dont_write_bytecode = True

import os
import pandas as pd
import numpy as np
from datetime import timedelta
import panel as pn
pn.extension('tabulator', sizing_mode="stretch_width")
import hvplot.pandas

import warnings
warnings.filterwarnings('ignore')

path = 'D:\Repos\PirnaCaseStudy'
sys.path.append(path)
import SMARTControl as sc
import git

'''
Pulling changes from github
still try this
'''

#git_dir = 'D:\Repos\PirnaCaseStudy'
#g = git.cmd.Git(git_dir)
#g.execute('git config pull.rebase false')
#g.pull()


'''

Define Parameters

'''

height = 580
min_width = 700
max_width = 1400

os.chdir(path)
database_fn = 'Data/Database.db'
Get = sc.queries.Get(database_fn)


'''
Querying the database
'''

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

# Check if HydroPlot goes and add it here
Get.HydroProfile()
HydroProfile_df = Get.HydroProfile_df.copy()
HydroProfile_df.columns = [
    'ID', 'PointID', 'DrillName', 'TestType', 'Unit', 'Depth', 'DrillDepth','MonitoringPoint', 'Value', 'E', 'N'
]


'''

Preparing Data for geological layers

'''
#handling log
HydroProfile_df.Depth *= -1
HydroProfile_df.Value = np.where(HydroProfile_df.Value < 0, 0, HydroProfile_df.Value)
# HydroProfile_df.Value  = np.log10 (HydroProfile_df.Value)    

plot_df = HydroProfile_df [
    (HydroProfile_df.TestType.isin (['EC logs', 'DPIL']))
].reset_index(drop = True)  

#Dataframe of interpreted layers
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
    
'''

Widgets

'''

#Map
value = end - timedelta(days=2) 
date_wid = pn.widgets.DatetimePicker(name='Date and time', start=start , end = end, value = value)
scalearrows_wid = pn.widgets.IntSlider(
    start = 1, end = 100 , step = 1, value = 10,
    name='Sizing arrows'
                                      )


#Scatter
wells_list = list(df.Name.unique())
wells_wid = pn.widgets.Select (name = 'Well', options = wells_list, value = wells_list[0])

#HydroProfile
drills_wid = pn.widgets.Select(name='Drill Name', options = list(HydroProfile_df.DrillName.unique()))



'''

Time Series

'''                                      
PALETTE = ["#00CED1", "#006400"]

    
g_df = df.groupby(['Name', pd.Grouper(freq='D')])['Value'].mean().to_frame().reset_index()
gr_df = r_df.groupby(['MonitoringPointName', pd.Grouper(freq='D')])['Value'].mean().to_frame().reset_index()
g_df = pd.concat ([g_df, gr_df])



# def iTS (wells_wid):

#     g1_df = g_df [
#         g_df.Name == wells_wid
#     ].reset_index(drop = True)  
    
    
#     return g1_df

# iBindTS = hvplot.bind(iTS, wells_wid).interactive()

# iScatterTS = iBindTS.hvplot.scatter(
#     x = 'Date', y = 'Value',
#     label = 'Diver Data',
#     # width = max_width,
#     alpha = 0.4, grid = True, size = 50,
#     ylabel = 'Hydraulic head (m)', xlabel = 'Time',
#     color = 'aqua', legend = True,
#                             )

# scatter_rg = gr_df.hvplot.scatter(
#     x='Date', y='Value',
#     ylabel = '[m]',
#     xlabel = 'Date', 
#     size = 50, 
#     # width = max_width,
#     height =500,
#     color = 'green',
#     label = "River Data",
#     alpha = 0.4, grid = True,
#     clabel = 'River head'
#     )

# iScatterTS =  scatter_rg * iScatterTS

def iTS (wells_wid):

    g1_df = g_df [
        g_df.Name == wells_wid
    ].reset_index(drop = True)  
    
    maxy , miny = 115, 107
    iScatterTS = g1_df.hvplot.scatter(
        
        x = 'Date', y = 'Value',
        label = 'Diver Data',
        # width = max_width,
        alpha = 0.4,
        grid = True, 
        size = 50,
        ylabel = 'Hydraulic head (m)', 
        xlabel = 'Time',
        color = 'aqua',
        legend = True,
        ylim= ( miny , maxy)
        
        )
    
    scatter_rg = gr_df.hvplot.scatter(
        
        x='Date', y='Value',
        ylabel = '[m]',
        xlabel = 'Date', 
        size = 50, 
        # width = max_width,
        height = 500,
        color = 'green',
        label = "River Data",
        alpha = 0.4, grid = True,
        clabel = 'River head',
        ylim= ( miny , maxy)
        )
    
    iScatterTS =  scatter_rg * iScatterTS
    
    return iScatterTS

iScatterTS = pn.bind(iTS, wells_wid)

# pn.Column(iBindTS).show()


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

        return pn.pane.plot.Folium(Map, height = height,
                                   
                                  )
    
    except Exception:
        
        return text

iMap = pn.bind(iPlot, date_wid, scalearrows_wid)

'''

Aquifer Characterization

'''


def iHPV(drills_wid):
    df =  plot_df [
        (plot_df.DrillName == drills_wid)
    ].reset_index(drop = True)  
        
    if df.shape[0] == 0:
        md=  pn.pane.Markdown ('''
        ### <center>No data for this drill</center>
        <br>
        ''',align = 'center', style = {'font-size' : '1.5em'})
        
        return pn.Row(md, width = 600)
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

        return iLineHP

    
#function for hydro stratigraphic layer
def iHPL(drills_wid): 
    
    df =  plot_df [
        (plot_df.DrillName == drills_wid)
    ].reset_index(drop = True)  

    df_ = layers_df [
        (layers_df.Drill== drills_wid)
    ].reset_index(drop = True)  

    #dropping columns that contain zero - getting rid of the layers that do not have landfills
    df_ = df_.loc [:,(df_ != 0).any(axis=0) ]
    
    if df_.shape[0] == 0:
        md=  pn.pane.Markdown ('''
        ### <center>No data for this drill</center>
        <br>
        ''',align = 'center', style = {'font-size' : '1.5em'})
        
        return pn.Row(md, width = 600)
    
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
        return iBarHP    


iLineHP = pn.bind(iHPV, drills_wid)
iBarHP = pn.bind(iHPL, drills_wid)


'''
Dashboard

app

'''
# Header
Inowas_fn = 'Assets/INOWASV1.png'
SMARTControl_fn = 'Assets/SmartControl.png'
dashboard_title = pn.panel('## SMART-Control')
header_c1 = pn.Column(pn.pane.PNG(Inowas_fn, height=40))
header_c2 = pn.Column(pn.pane.PNG('Assets/SmartControl.png', height=40))

header = pn.Row(
    header_c1,
    pn.Spacer(width=450),
    header_c2,
    background='aqua',
    height = 50,
    height_policy = 'fixed',
    sizing_mode = 'stretch_width',
    min_width = min_width,
    max_width = max_width
              )

## Elements

### Map
Map_r1 = pn.Row(date_wid , scalearrows_wid)
Map_r2 = pn.Row(iMap)
Map_c = pn.Column(
    Map_r1, Map_r2,
    height_policy = 'fit',
    sizing_mode = 'stretch_width',
    min_width = min_width,
    max_width = max_width
                    )

# Map_c.show()

### Time Series
TS_r1 = pn.Row (wells_wid)
TS_r2 = pn.Column (iScatterTS)


TS_c = pn.Column (
    TS_r1, TS_r2,
    height_policy = 'fit',
    sizing_mode = 'stretch_width',
    min_width = min_width,
    max_width = max_width
    )

### Aquifer characterization  (AC)
AC_r1 = pn.Row (drills_wid)
AC_r2 = pn.Row(
    pn.layout.HSpacer(width = 200), 
    pn.Row(iLineHP,  max_width = 500, min_width = 600),
    pn.Row (iBarHP,  max_width = 200),
    pn.layout.HSpacer(width = 200), 
    min_width = min_width,
    max_width = max_width
)

AC_c = pn.Column (AC_r1,AC_r2,
                  min_width = min_width, 
                  max_width = max_width
                  )


#Tabs
body = pn.Tabs (
    ('Groundwater Flow', Map_c) ,
    ('Hydrostratigraphy', AC_c), 
    ('Time series', TS_c),
    )

    


#Bottom
Groundwatch_fn = 'Assets/Groundwatchv1.png'
Python_fn = 'Assets/Python-logo-notext.png'
PegelAlarm_fn = 'Assets/PegelAlarm.png'
TUDresden_fn = 'Assets/TuDresden.png'

col1_r3 = pn.Column(pn.pane.PNG(Groundwatch_fn, height=40))
col2_r3 = pn.Column(pn.pane.PNG(Python_fn, height=40))
col3_r3 = pn.Column(pn.pane.PNG(PegelAlarm_fn, height=40))
col4_r3 = pn.Column(pn.pane.PNG(TUDresden_fn, height=40))


bottom = pn.Row(
    col1_r3, col2_r3 , col3_r3, col4_r3, 
    background='turquoise',
    height = 50,
    min_width = min_width,
    max_width = max_width
)

dashboard = pn.Column(header ,body, bottom)
# dashboard = pn.Column(bottom_r3)


dashboard.show()
# body_r2.show()